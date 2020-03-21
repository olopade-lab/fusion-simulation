#!/bin/bash

FUSIONS_PER_SAMPLE=$1
READS_PER_SAMPLE=$2

FusionSimulatorToolkit/FusionTranscriptSimulator \
  /gencode_annotation \
  /reference_genome $FUSIONS_PER_SAMPLE 1> /output_data/fusions.fasta 2> /dev/null

cat /output_data/fusions.fasta /reference_cdna > /output_data/combined.transcripts.fasta

$TRINITY_HOME/util/align_and_estimate_abundance.pl \
  --transcripts /output_data/combined.transcripts.fasta \
  --est_method RSEM \
  --aln_method bowtie \
  --prep_reference \
  --seqType fq \
  --left /left_fq \
  --right /right_fq \
  --output_dir /output_data/RSEM

FusionSimulatorToolkit/simulate_fusion_trans_expr_vals.pl \
  /output_data/RSEM/RSEM.isoforms.results \
  /output_data/combined.transcripts.fasta \
  > /output_data/target.forSimulation.RSEM.isoforms.results

rsem-simulate-reads /ouput_data/combined.transcripts.fasta.RSEM \
  /output_data/RSEM/RSEM.stat/RSEM.model \
  /output_data/target.forSimulation.RSEM.isoforms.results \
  0.01 \
  $READS_PER_SAMPLE \
  /output_data/sim_reads

FusionSimulatorToolkit/util/rename_fq_reads_by_target_trans_acc.direct.pl \
  /output_data/combined.transcripts.fasta.RSEM.idx.fa \
  /output_data/sim_reads_1.fq /output_data/sim_reads_2.fq
