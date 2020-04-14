nohup python run.py \
  --sample_dirs '/cephfs/users/annawoodard/gene-fusion/data/interim/LIB*' \
  --left *R1* \
  --right *R2* \
  --gencode_annotation /cephfs/users/annawoodard/fusion-simulation/data/external/FusionSimulatorToolkit/RESOURCES/gencode.v19.annotation.gff3 \
  --reference_genome /cephfs/users/annawoodard/fusion-simulation/data/external/GRCh38_gencode_v31_CTAT_lib_Oct012019.plug-n-play/ctat_genome_lib_build_dir/ref_genome.fa \
  --reference_cdna /cephfs/users/annawoodard/fusion-simulation/data/external/GRCh38_gencode_v31_CTAT_lib_Oct012019.plug-n-play/ctat_genome_lib_build_dir/ref_annot.cdna.fa \
  --fusions_per_sample 30 \
  --reads_per_sample 3000000 \
  --replicates 3 \
  --out_dir /cephfs/users/annawoodard/fusion-simulation/data/processed \
  > run.log &
