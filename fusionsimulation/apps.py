import parsl
from parsl.app.app import bash_app, python_app


@python_app(cache=True)
def parse_gene_id_to_gene_name_map(annotation_gff3_path):
    import os
    import pandas as pd

    annotation = pd.read_csv(annotation_gff3_path, sep='\t', comment='#', usecols=[8], names=['attributes'])
    annotation['attributes'] = [i.split(';') for i in annotation.attributes]

    for a in ['gene_id', 'gene_name']:
        annotation[a] = [y.split('=')[1] for x in annotation.attributes for y in x if y.startswith(a)]
    annotation.drop(columns=['attributes'], inplace=True)
    annotation.drop_duplicates(subset='gene_id', inplace=True)
    annotation = annotation.set_index('gene_id')

    out_path = os.path.splitext(annotation_gff3_path)[0] + '.gene_id_to_gene_name_map.pkl'
    annotation.to_pickle(out_path)

    return out_path

@python_app(cache=True)
def make_truth_set(gene_id_to_gene_name_map_path, fasta, sample, inputs=[]):
    import pandas as pd
    import os

    annotation = pd.read_pickle(gene_id_to_gene_name_map_path)

    num_lines = sum(1 for line in open(fasta))
    fusions = pd.read_csv(fasta, sep='\t', skiprows=range(1, num_lines + 1, 2), header=None, names=['gene_id_pair'])
    fusions.gene_id_pair = [i.split(' ')[0].replace('>', '') for i in fusions.gene_id_pair]

    fusions['left_gene_id'] = [i.split('--')[0] for i in fusions.gene_id_pair]
    fusions['right_gene_id'] = [i.split('--')[1] for i in fusions.gene_id_pair]
    fusions = fusions.join(annotation, on='left_gene_id').rename(columns={'gene_name': 'left_gene_name'})
    fusions = fusions.join(annotation, on='right_gene_id').rename(columns={'gene_name': 'right_gene_name'})
    fusions['fusion'] = fusions[['left_gene_name', 'right_gene_name']].apply(
        lambda x: '--'.join([str(i) for i in x]), axis=1)
    fusions['sample'] = sample

    fusions.to_pickle(os.path.join(os.path.dirname(fasta), 'truth.pkl'))

@bash_app(cache=True)
def simulate_fusions(
        output_data,
        gencode_annotation,
        reference_genome,
        reference_cdna,
        fusions_per_sample,
        left_fq,
        right_fq,
        reads_per_sample,
        container_type='singularity',
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME):
    import os

    command = ['echo $HOSTNAME; mkdir -p {output_data}; ']
    if container_type == 'docker':
        command += [
            'docker run',
            '--rm',
            '-v {left_fq}:/left_fq:ro',
            '-v {right_fq}:/right_fq:ro',
            '-v {output_data}:/output_data ',
            '-v {gencode_annotation}:/gencode_annotation:ro ',
            '-v {reference_genome}:/reference_genome:ro ',
            '-v {reference_cdna}:/reference_cdna:ro ',
            'olopadelab/fusion-simulation:latest',
        ]
    elif container_type == 'singularity':
        command += [
            'singularity exec',
            '-B {left_fq}:/left_fq',
            '-B {right_fq}:/right_fq',
            '-B {output_data}:/output_data',
            '-B {gencode_annotation}:/gencode_annotation',
            '-B {reference_genome}:/reference_genome',
            '-B {reference_cdna}:/reference_cdna',
            '{base_dir}/docker/fusion-simulation.sif'
        ]
    else:
        raise RuntimeError('Container type must be either docker or singularity')

    command += [
        'run.sh {fusions_per_sample} {reads_per_sample}'
    ]

    return ' '.join(command).format(
        base_dir='/'.join(os.path.abspath(__file__).split('/')[:-2]),
        output_data=output_data,
        gencode_annotation=gencode_annotation,
        reference_genome=reference_genome,
        reference_cdna=reference_cdna,
        left_fq=left_fq,
        right_fq=right_fq,
        fusions_per_sample=fusions_per_sample,
        reads_per_sample=reads_per_sample
    )


@bash_app
def generate_fusions(
        output_data,
        gencode_annotation,
        reference_genome,
        reference_cdna,
        fusions_per_sample,
        image='olopadelab/fusion-simulation',
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME):

    import os
    os.makedirs(output_data, exist_ok=True)

    command = (
        'echo $HOSTNAME; '
        'docker run '
        '--rm '
        '-v {output_data}:/output_data '
        '-v {gencode_annotation}:/gencode_annotation:ro '
        '-v {reference_genome}:/reference_genome:ro '
        '{image} '
        'bash -c "'
            'FusionSimulatorToolkit/FusionTranscriptSimulator '
            '/gencode_annotation '
            '/reference_genome {fusions_per_sample} 1> /output_data/fusions.fasta 2> /dev/null'
        '"; '
        'cat {output_data}/fusions.fasta {reference_cdna} > {output_data}/combined.transcripts.fasta'
    )

    return command.format(
        output_data=output_data,
        gencode_annotation=gencode_annotation,
        reference_genome=reference_genome,
        reference_cdna=reference_cdna,
        image=image,
        fusions_per_sample=fusions_per_sample
    )


@bash_app
def estimate_abundance_and_simulate_reads(
        left_fq,
        right_fq,
        output_data,
        reads_per_sample,
        image='olopadelab/fusion-simulation',
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME,
        inputs=[]):

    quantify_transcripts = (
        '$TRINITY_HOME/util/align_and_estimate_abundance.pl '
        '--transcripts /output_data/combined.transcripts.fasta '
        '--est_method RSEM '
        '--aln_method bowtie '
        '--prep_reference '
        '--seqType fq '
        '--left /left_fq '
        '--right /right_fq '
        '--output_dir /output_data/RSEM '
    )

    simulate_expression_levels = (
        'FusionSimulatorToolkit/simulate_fusion_trans_expr_vals.pl '
        '/output_data/RSEM/RSEM.isoforms.results '
        '/output_data/combined.transcripts.fasta '
        '> /output_data/target.forSimulation.RSEM.isoforms.results '
    )

    simulate_reads = (
        'rsem-simulate-reads /ouput_data/combined.transcripts.fasta.RSEM '
        '/output_data/RSEM/RSEM.stat/RSEM.model '
        '/output_data/target.forSimulation.RSEM.isoforms.results '
        '0.01  {reads_per_sample} '
        '/output_data/sim_reads '
    ).format(reads_per_sample=reads_per_sample)

    rename_reads = (
        'FusionSimulatorToolkit/util/rename_fq_reads_by_target_trans_acc.direct.pl '
        '/output_data/combined.transcripts.fasta.RSEM.idx.fa '
        '/output_data/sim_reads_1.fq /output_data/sim_reads_2.fq '
    )

    command = (
        'docker run '
        '--rm '
        '-v {left_fq}:/left_fq:ro '
        '-v {right_fq}:/right_fq:ro '
        '-v {output_data}:/output_data '
        '{image} '
        'bash -c "'
    ).format(
        left_fq=left_fq,
        right_fq=right_fq,
        output_data=output_data,
        image=image
    ) + '; '.join(
            [
                quantify_transcripts,
                simulate_expression_levels,
                simulate_reads,
                rename_reads
            ]
    ) + '"'

    return command
