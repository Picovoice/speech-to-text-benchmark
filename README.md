# Speech-to-Text Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This repo is a minimalist and extensible framework for benchmarking different speech-to-text engines.

## Table of Contents

-[Data](#data)
-[Metrics](#metrics)
-[Engines](#engines)
    - [Amazon Transcribe](#amazon-transcribe)
    - [Google Speech-to-Text](#google-speech-to-text)
    - [Mozilla DeepSpeech](#mozilla-deepspeech)
    - [Picovoice Cheetah](#picovoice-cheetah)
    - [Picovoice Leopard](#picovoice-leopard)
-[Usage](#usage)
-[Results](#results)

## Data

[LibriSpeech](http://www.openslr.org/12/) dataset is used for benchmarking.

## Metrics

### Word Error Rate

Word error rate (WER) is the ratio of Levenstein distance between words in a reference transcript and the words in the
output of the speech-to-text engine to the number of words in the reference transcript.

### Real Time Factor

Real-time factor (RTF) is the ratio of CPU (processing) time to the length of the input speech file. A speech-to-text
engine with lower RTF is more computationally efficient. We omit this metric for cloud-based engines.

### Model Size

The aggregate size of models (acoustic and language), in MB. We omit this metric for cloud-based engines.

## Engines

### Amazon Transcribe

Amazon Transcribe is a cloud-based speech recognition engine, offered by AWS.

### Google Speech-to-Text

A cloud-based speech recognition engine offered by Google Cloud Platform.

### Mozilla DeepSpeech

[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open-source implementation of
[Baidu's DeepSpeech](https://arxiv.org/abs/1412.5567) by Mozilla. The version used in this benchmark is `0.9.3`.

### Picovoice Cheetah

[Cheetah](https://github.com/Picovoice/cheetah) is a streaming speech-to-text engine developed by
[Picovoice](http://picovoice.ai/).

### Picovoice Leopard

[Leopard](https://github.com/Picovoice/leopard) is a speech-to-text engine developed by
[Picovoice](http://picovoice.ai/).

## Usage

Below is information on how to use this framework to benchmark the speech-to-text engines. 

1. Make sure that you have installed DeepSpeech and PocketSphinx on your machine by following the instructions on their official pages.
1. Unpack
DeepSpeech's models under [resources/deepspeech](/res/deepspeech).
1. Download the [test-clean](http://www.openslr.org/resources/12/test-clean.tar.gz) portion of LibriSpeech and unpack it under
[resources/data](/res/data).
1. For running Google Speech-to-Text and Amazon Transcribe, you need to sign up for the respective cloud provider
and setup permissions / credentials according to their documentation. Running these services may incur fees.

Word Error Rate can be measured by running the following command from the root of the repository: 

```bash
python benchmark.py --engine_type AN_ENGINE_TYPE
```

The valid options for the `engine_type`
parameter are: `AMAZON_TRANSCRIBE`, `CMU_POCKET_SPHINX`, `GOOGLE_SPEECH_TO_TEXT`, `MOZILLA_DEEP_SPEECH`,
`PICOVOICE_CHEETAH`, `PICOVOICE_CHEETAH_LIBRISPEECH_LM`, `PICOVOICE_LEOPARD`, and `PICOVOICE_LEOPARD_LIBRISPEECH_LM`.

`PICOVOICE_CHEETAH_LIBRISPEECH_LM` is the same as `PICOVOICE_CHEETAH`
except that the language model is trained on LibriSpeech training text similar to
[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech/tree/master/data/lm). The same applies to Leopard.

## Results

The below results are obtained by following the previous steps. The benchmarking was performed on a Linux machine running
Ubuntu 18.04 with 64GB of RAM and an Intel i5-6500 CPU running at 3.2 GHz. WER refers to word error rate and RTF refers to
real time factor.

| Engine | WER | RTF (Desktop) | RTF (Raspberry Pi 3) | RTF (Raspberry Pi Zero) | Model Size (Acoustic and Language) |
:---:|:---:|:---:|:---:|:---:|:---:
Amazon Transcribe | 8.21% | N/A | N/A | N/A | N/A |
CMU PocketSphinx (0.1.15) | 31.82% | 0.32 | 1.87 | **2.04** | 97.8 MB |
Google Speech-to-Text | 12.23% | N/A | N/A | N/A | N/A |
Mozilla DeepSpeech | 7.55% | 0.46  | N/A | N/A | 1146.8 MB |
Picovoice Leopard | 5.73% | **0.02** | **0.55** | 2.55 | 47.9 MB |

The figure below compares the word error rate of speech-to-text engines. For Picovoice, we included the engine that was
trained on LibriSpeech training data similar to Mozilla DeepSpeech.

![](res/doc/word_error_rate_comparison.png)

The figure below compares accuracy and runtime metrics of offline speech-to-text engines. For Picovoice we included the
engines that were trained on LibriSpeech training data similar to Mozilla DeepSpeech. Leopard achieves the highest accuracy
while being 23X faster and 27X smaller in size compared to second most accurate engine (Mozilla DeepSpeech).

![](res/doc/offline_stt_comparison.png)
