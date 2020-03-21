import argparse
import os
import glob

import parsl
from igsb import config

parsl.set_stream_logger()
parsl.load(config)

from apps import generate_fusions, estimate_abundance_and_simulate_reads


parser = argparse.ArgumentParser()
parser.add_argument("--sample_dirs", help="")
parser.add_argument("--left", help="")
parser.add_argument("--right", help="")
parser.add_argument("--gencode_annotation", help="")
parser.add_argument("--reference_cdna", help="")
parser.add_argument("--reference_genome", help="")
parser.add_argument("--fusions_per_sample", help="fusions to simulate per sample")
parser.add_argument("--reads_per_sample", help="reads to simulate per sample")
parser.add_argument("--out_dir", default=None)

args = parser.parse_args()

base_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])
if args.out_dir is None:
    args.out_dir = os.path.join(base_dir, 'data', 'processed')

sample_dirs = glob.glob(args.sample_dirs)

for sample_dir in sample_dirs:
    print(sample_dir)
    sample_id = os.path.split(sample_dir)[-1]
    output_data = os.path.join(args.out_dir, sample_id)
    print('submitting tasks for sample {}'.format(sample_id))

    fusions = generate_fusions(
        output_data,
        args.gencode_annotation,
        args.reference_genome,
        args.reference_cdna,
        args.fusions_per_sample,
        image='olopadelab/fusion-simulation',
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME
    )

    left_fq = glob.glob(os.path.join(sample_dir, args.left))
    right_fq = glob.glob(os.path.join(sample_dir, args.right))
    if (len(left_fq) > 1) or (len(right_fq) > 1):
        raise RuntimeError('Only one input fastq per sample supported!')

    estimate_abundance_and_simulate_reads(
        left_fq[0],
        right_fq[0],
        output_data,
        args.reads_per_sample,
        image='olopadelab/fusion-simulation',
        stderr=parsl.AUTO_LOGNAME,
        stdout=parsl.AUTO_LOGNAME,
        inputs=[fusions]
    )

parsl.wait_for_current_tasks()

print('finished processing!')
