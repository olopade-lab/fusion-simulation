nohup python run.py \
  --sample_dirs '/scratch/midway2/annawoodard/polyfuse/data/interim/*' \
  --left *R1* \
  --right *R2* \
  --gencode_annotation /scratch/midway2/annawoodard/data/external/GRCh38_gencode_v33_CTAT_lib_Apr062020.plug-n-play/ctat_genome_lib_build_dir/gencode.v33.annotation.gff3 \
  --reference_genome /scratch/midway2/annawoodard/data/external/GRCh38_gencode_v33_CTAT_lib_Apr062020.plug-n-play/ctat_genome_lib_build_dir/ref_genome.fa \
  --reference_cdna /scratch/midway2/annawoodard/data/external/GRCh38_gencode_v33_CTAT_lib_Apr062020.plug-n-play/ctat_genome_lib_build_dir/ref_annot.cdna.fa \
  --fusions_per_sample 500 \
  --reads_per_sample 30000000 \
  --config /scratch/midway2/annawoodard/fusion-simulation/fusionsimulation/configs/midway.py \
  &> run.log &
