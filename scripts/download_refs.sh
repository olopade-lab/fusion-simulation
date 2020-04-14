#!/bin/bash

CTAT_LIB=GRCh38_gencode_v33_CTAT_lib_Apr062020.plug-n-play.tar.gz


mkdir -p ../data/external
cd ../data/external
wget https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/$CTAT_LIB
tar xzf $CTAT_LIB
rm $CTAT_LIB
wget ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_33/gencode.v33.annotation.gff3.gz
gunzip gencode.v33.annotation.gff3.gz
mv gencode.v33.annotation.gff3 ctat_genome_lib_build_dir
cd -
