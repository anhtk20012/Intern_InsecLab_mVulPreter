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

cd ~/
if [[ ! -d joern-cli_v1.1.172 ]]; then
    wget https://github.com/joernio/joern/releases/download/v1.1.172/joern-cli.zip
    unzip joern-cli.zip
    rm joern-cli.zip
    mv joern-cli joern-cli_v1.1.172
else
    echo "Already downloaded Joern v1.1.172"
fi