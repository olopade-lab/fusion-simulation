import argparse
import os
import glob
import importlib

import parsl

parsl.set_stream_logger()

from fusionsimulation.apps import simulate_fusions, parse_gene_id_to_gene_name_map, make_truth_set


parser = argparse.ArgumentParser()
parser.add_argument("--sample_dirs", help="")
parser.add_argument("--left", help="")
parser.add_argument("--right", help="")
parser.add_argument("--gencode_annotation", help="")
parser.add_argument("--reference_cdna", help="")
parser.add_argument("--reference_genome", help="")
parser.add_argument("--fusions_per_sample", help="fusions to simulate per sample")
parser.add_argument("--reads_per_sample", help="reads to simulate per sample")
# parser.add_argument("--replicates", type=int, help="reads to simulate per sample")
parser.add_argument("--out_dir", default=None)
parser.add_argument("--container_type", default='singularity')
parser.add_argument("--config", default=None, help="Parsl config to parallelize with")
args = parser.parse_args()

base_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])
if args.out_dir is None:
    args.out_dir = os.path.join(base_dir, 'data', 'processed')
if args.config is None:
    args.config = os.path.join(base_dir, 'fusionsimulation', 'configs', 'local.py')

spec = importlib.util.spec_from_file_location('', args.config)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
parsl.load(module.config)

if args.container_type == 'singularity':
    image_path = '{base_dir}/docker/fusion-simulation.sif'.format(base_dir=base_dir)
    # FIXME may require too much memory on some machines
    if not os.path.isfile(image_path):
        print('downloading {}'.format(image_path))
        subprocess.call(
            'singularity build {image_path} docker://olopadelab/fusion-simulation'.format(
                image_path=image_path),
            shell=True
        )

gene_id_to_gene_name_map_path = parse_gene_id_to_gene_name_map(args.gencode_annotation)

sample_dirs = glob.glob(args.sample_dirs)
for sample_dir in sample_dirs:
    sample_id = os.path.split(sample_dir)[-1]
    output_data = os.path.join(args.out_dir, sample_id)
    print('submitting tasks for sample {}'.format(sample_id))

    left_fq = glob.glob(os.path.join(sample_dir, args.left))
    right_fq = glob.glob(os.path.join(sample_dir, args.right))
    if (len(left_fq) > 1) or (len(right_fq) > 1):
        raise RuntimeError('Only one input fastq per sample supported!')

    fusions = simulate_fusions(
        output_data,
        args.gencode_annotation,
        args.reference_genome,
        args.reference_cdna,
        args.fusions_per_sample,
        left_fq[0],
        right_fq[0],
        args.reads_per_sample,
        container_type=args.container_type,
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME
    )

    make_truth_set(
        gene_id_to_gene_name_map_path,
        os.path.join(output_data, 'fusions.fasta'),
        sample_dir.split('/')[-1],
        inputs=[fusions]
    )

parsl.wait_for_current_tasks()

print('finished processing!')
