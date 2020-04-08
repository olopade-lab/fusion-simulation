#!/bin/bash

CTAT_LIB=GRCh38_gencode_v32_CTAT_lib_Dec062019.plug-n-play.tar.gz

mkdir -p ../data/external
cd ../data/external
wget https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/$CTAT_LIB
tar xzf $CTAT_LIB
rm $CTAT_LIB
cd -
