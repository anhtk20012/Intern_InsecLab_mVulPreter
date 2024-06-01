#!/bin/bash
if [[ -d dataset/raw_data ]]; then
    echo "Foler dataset exists, starting download"
else
    mkdir --parents dataset/raw_data
fi

cd dataset/raw_data

if [[ ! -f "MSR_data_cleaned.csv" ]]; then
    gdown https://drive.google.com/uc?id=1-0VhnHBp9IGh90s2wCNjeCMuy70HPl8X
    unzip MSR_data_cleaned.zip
    rm MSR_data_cleaned.zip
else
    echo "Already downloaded bigvul data"
fi

