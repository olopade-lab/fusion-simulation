import argparse
import os
import glob

import parsl
from igsb import config

parsl.set_stream_logger()
parsl.load(config)

from apps import simulate_fusions


parser = argparse.ArgumentParser()
parser.add_argument("--sample_dirs", help="")
parser.add_argument("--left", help="")
parser.add_argument("--right", help="")
parser.add_argument("--gencode_annotation", help="")
parser.add_argument("--reference_cdna", help="")
parser.add_argument("--reference_genome", help="")
parser.add_argument("--fusions_per_sample", help="fusions to simulate per sample")
parser.add_argument("--reads_per_sample", help="reads to simulate per sample")
parser.add_argument("--replicates", type=int, help="reads to simulate per sample")
parser.add_argument("--out_dir", default=None)

args = parser.parse_args()

base_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])
if args.out_dir is None:
    args.out_dir = os.path.join(base_dir, 'data', 'processed')

sample_dirs = glob.glob(args.sample_dirs)

for sample_dir in sample_dirs:
    print(sample_dir)
    sample_id = os.path.split(sample_dir)[-1]
    for replicate in range(0, args.replicates):
        output_data = os.path.join(args.out_dir, '{}_{}'.format(sample_id, replicate + 1))
        print('submitting tasks for sample {}, replicate {}'.format(sample_id, replicate + 1))

        left_fq = glob.glob(os.path.join(sample_dir, args.left))
        right_fq = glob.glob(os.path.join(sample_dir, args.right))
        if (len(left_fq) > 1) or (len(right_fq) > 1):
            raise RuntimeError('Only one input fastq per sample supported!')

        simulate_fusions(
            output_data,
            args.gencode_annotation,
            args.reference_genome,
            args.reference_cdna,
            args.fusions_per_sample,
            left_fq[0],
            right_fq[0],
            args.reads_per_sample,
            image='olopadelab/fusion-simulation',
            stderr=parsl.AUTO_LOGNAME,
            stdout=parsl.AUTO_LOGNAME
        )


parsl.wait_for_current_tasks()

print('finished processing!')
