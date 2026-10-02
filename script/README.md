# Speech-to-Text Benchmark Scripts

## Dataset Download

We provide a script to download HuggingFace hosted datasets into the expected format.
The script supports the following dataset:

- Fleurs
- JSUT BASIC

Replace `${DATASET}` with a supported dataset (`FLEURS`, `JSUT_BASIC`), `${LANGUAGE}` with a supported language and `${DOWNLOAD_FOLDER}` with the output download folder path.

```
python3 -m script.download_datasets \
--dataset ${DATASET} \
--language ${LANGUAGE} \
--download-folder ${DOWNLOAD_FOLDER}
```

## Alignment Dataset Generation

### Montreal Forced Aligner Setup

1. Follow [these instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to install Conda
2. Setup the environment with `conda install -c conda-forge montreal-forced-aligner`
3. Download the acoustic model with `mfa model download acoustic ${ACOUSTIC_MODEL_NAME}`
    - Replace `${ACOUSTIC_MODEL_NAME}` with `english_us_arpa` for English
    - Other languages can be found [here](https://mfa-models.readthedocs.io/en/latest/acoustic/index.html#acoustic)
4. Download the dictionary with `mfa model download dictionary ${DICTIONARY_NAME}`
    - Replace `${DICTIONARY_NAME}` with `english_us_arpa` for English
    - Other languages can be found [here](https://mfa-models.readthedocs.io/en/latest/dictionary/index.html#dictionary)

### Usage

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with the path to the dataset, `${LANGUAGE}` with the target language, `${OUTPUT_FOLDER}` with the output folder path and `${NUM_EXAMPLES}` with the number of files to process.

```
python3 -m script.generate_alignments \
    --dataset ${DATASET} \
    --dataset-folder ${DATASET_FOLDER} \
    --language ${LANGUAGE} \
    --output-folder ${OUTPUT_FOLDER} \
    --num-examples ${NUM_EXAMPLES}
```

