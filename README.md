# Speech-to-Text Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This repo is a minimalist and extensible framework for benchmarking different speech-to-text engines.

## Table of Contents

- [Data](#data)
- [Metrics](#metrics)
- [Engines](#engines)
- [Usage](#usage)
- [Results](#results)

## Data

- [LibriSpeech](http://www.openslr.org/12/)
- [TED-LIUM](https://www.openslr.org/7/)
- [Common Voice](https://commonvoice.mozilla.org/en)

## Metrics

### Word Error Rate

Word error rate (WER) is the ratio of edit distance between words in a reference transcript and the words in the output
of the speech-to-text engine to the number of words in the reference transcript.

### Core-Hour

The Core-Hour metric is used to evaluate the computational efficiency of the speech-to-text engine,
indicating the number of CPU hours required to process one hour of audio. A speech-to-text
engine with lower Core-Hour is more computationally efficient. We omit this metric for cloud-based engines.

### Model Size

The aggregate size of models (acoustic and language), in MB. We omit this metric for cloud-based engines.

## Engines

- [Amazon Transcribe](https://aws.amazon.com/transcribe/)
- [Azure Speech-to-Text](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/)
- [Google Speech-to-Text](https://cloud.google.com/speech-to-text)
- [IBM Watson Speech-to-Text](https://www.ibm.com/ca-en/cloud/watson-speech-to-text)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Picovoice Cheetah](https://picovoice.ai/)
- [Picovoice Leopard](https://picovoice.ai/)

## Usage

This benchmark has been developed and tested on `Ubuntu 20.04`.

- Install [FFmpeg](https://www.ffmpeg.org/)
- Download datasets.
- Install the requirements:

```console
pip3 install -r requirements.txt
```

### Amazon Transcribe Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and `${AWS_PROFILE}`
with the name of AWS profile you wish to use.

```console
python3 benchmark.py \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--engine AMAZON_TRANSCRIBE \
--aws-profile ${AWS_PROFILE}
```

### Azure Speech-to-Text Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset,
`${AZURE_SPEECH_KEY}` and `${AZURE_SPEECH_LOCATION}` information from your Azure account.

```console
python3 benchmark.py \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--engine AZURE_SPEECH_TO_TEXT \
--azure-speech-key ${AZURE_SPEECH_KEY}
--azure-speech-location ${AZURE_SPEECH_LOCATION}
```

### Google Speech-to-Text Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and
`${GOOGLE_APPLICATION_CREDENTIALS}` with credentials download from Google Cloud Platform.

```console
python3 benchmark.py \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--engine GOOGLE_SPEECH_TO_TEXT \
--google-application-credentials ${GOOGLE_APPLICATION_CREDENTIALS}
```

### IBM Watson Speech-to-Text Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and
`${WATSON_SPEECH_TO_TEXT_API_KEY}`/`${${WATSON_SPEECH_TO_TEXT_URL}}` with credentials from your IBM account.

```console
python3 benchmark.py \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--engine IBM_WATSON_SPEECH_TO_TEXT \
--watson-speech-to-text-api-key ${WATSON_SPEECH_TO_TEXT_API_KEY}
--watson-speech-to-text-url ${WATSON_SPEECH_TO_TEXT_URL}
```

### OpenAI Whisper Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and
`${WHISPER_MODEL}` with the whisper model type (`WHISPER_TINY`, `WHISPER_BASE`, `WHISPER_SMALL`,
`WHISPER_MEDIUM`, or `WHISPER_LARGE`)

```console
python3 benchmark.py \
--engine ${WHISPER_MODEL} \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
```

### Picovoice Cheetah Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and
`${PICOVOICE_ACCESS_KEY}` with AccessKey obtained from [Picovoice Console](https://console.picovoice.ai/).

```console
python3 benchmark.py \
--engine PICOVOICE_CHEETAH \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--picovoice-access-key ${PICOVOICE_ACCESS_KEY}
```

### Picovoice Leopard Instructions

Replace `${DATASET}` with one of the supported datasets, `${DATASET_FOLDER}` with path to dataset, and
`${PICOVOICE_ACCESS_KEY}` with AccessKey obtained from [Picovoice Console](https://console.picovoice.ai/).

```console
python3 benchmark.py \
--engine PICOVOICE_LEOPARD \
--dataset ${DATASET} \
--dataset-folder ${DATASET_FOLDER} \
--picovoice-access-key ${PICOVOICE_ACCESS_KEY}
```

## Results

### Word Error Rate (WER)

![](results/plots/WER.png)

|              Engine              | LibriSpeech test-clean | LibriSpeech test-other | TED-LIUM | CommonVoice | Average |
|:--------------------------------:|:----------------------:|:----------------------:|:--------:|:-----------:|:-------:|
|        Amazon Transcribe         |          2.7%          |          5.7%          |   3.9%   |    8.8%     |  5.3%   |
|       Azure Speech-to-Text       |          3.0%          |          6.4%          |   4.7%   |    9.0%     |  5.8%   |
|      Google Speech-to-Text       |         11.0%          |         24.7%          |  14.5%   |    32.0%    |  20.5%  |
| Google Speech-to-Text (Enhanced) |          6.3%          |         13.3%          |   6.2%   |    18.3%    |  11.0%  |
|    IBM Watson Speech-to-Text     |         11.0%          |         26.4%          |  11.8%   |    39.5%    |  22.2%  |
|           Whisper Tiny           |          6.2%          |         14.1%          |   6.7%   |   24.52%    |  12.8%  |
|           Whisper Base           |          4.5%          |         10.7%          |   5.5%   |    18.4%    |  9.7%   |
|          Whisper Small           |          3.6%          |          7.5%          |   4.8%   |    12.8%    |  7.2%   |
|          Whisper Medium          |          3.5%          |          6.5%          |   4.7%   |    10.3%    |  6.3%   |
|   Whisper Large (Multilingual)   |          3.9%          |          5.7%          |   4.7%   |    12.1%    |  6.7%   |
|        Picovoice Cheetah         |          5.9%          |         12.5%          |   7.8%   |    17.5%    |  10.9%  |
|        Picovoice Leopard         |          5.6%          |         11.6%          |   7.3%   |    16.3%    |  10.2%  |

### Core-Hour & Model Size

To obtain these results, we ran the benchmark across the entire TED-LIUM dataset and recorded the processing time.
The measurement is carried out on an Ubuntu 22.04 machine with AMD CPU (`AMD Ryzen 9 5900X (12) @ 3.70GHz`),
64 GB of RAM, and NVMe storage, using 10 cores simultaneously. We omit Whisper Large (Multilingual) from this benchmark.

|      Engine       | Core-Hour | Model Size / MB |
|:-----------------:|:---------:|:---------------:|
| Picovoice Leopard |   0.05    |       36        |
| Picovoice Cheetah |   0.09    |       31        |
|  Whisper Medium   |   1.50    |      1457       |
|   Whisper Small   |   0.89    |       462       |
|   Whisper Base    |   0.28    |       139       |
|   Whisper Tiny    |   0.15    |       73        |

![](results/plots/cpu_usage_comparison.png)
