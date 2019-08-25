# Speech-to-Text Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This is a minimalist and extensible framework for benchmarking different speech-to-text engines. It has been developed
and tested on Ubuntu using Python3.

## Table of Contents

* [Background](#background)
* [Data](#data)
* [Metrics](#metrics)
    * [Word Error Rate](#word-error-rate)
    * [Real Time Factor](#real-time-factor)
    * [Model Size](#model-size)
* [Speech-to-Text Engines](#speech-to-text-engines)
    * [Amazon Transcribe](#amazon-transcribe)
    * [CMU PocketSphinx](#cmu-pocketsphinx)
    * [Google Speech-to-Text](#google-speech-to-text)
    * [Mozilla DeepSpeech](#mozilla-deepspeech)
    * [Picovoice Cheetah](#picovoice-cheetah)
* [Usage](#usage)
    * [Word Error Rate Measurement](#word-error-rate-measurement)
    * [Real Time Factor Measurement](#real-time-factor-measurement)
* [Results](#results)
* [License](#license)

## Background

This framework has been developed by [Picovoice](http://picovoice.ai/) as part of the
[Cheetah](https://github.com/Picovoice/cheetah) project. Cheetah is Picovoice's speech-to-text engine, specifically designed to
run efficiently on the edge (offline). Deep learning has been the main driver in recent improvements in speech recognition but due to stringent compute/storage limitations of IoT platforms, it is mostly beneficial to cloud-based engines. Picovoice's
proprietary deep learning technology enables transferring these improvements to IoT platforms with significantly lower CPU/memory footprint.

## Data

[LibriSpeech](http://www.openslr.org/12/) dataset is used for benchmarking. We use the
[test-clean](http://www.openslr.org/resources/12/test-clean.tar.gz) portion.

## Metrics

This benchmark considers three metrics: word error rate, real-time factor, and model size.

### Word Error Rate

Word error rate (WER) is defined as the ratio of [Levenstein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
between words in a reference transcript and words in the output of the speech-to-text engine, to the number of
words in the reference transcript.

### Real Time Factor

Real time factor (RTF) is measured as the ratio of CPU (processing) time to the length of the input speech file. A
speech-to-text engine with lower RTF is more computationally efficient. We omit this metric for cloud-based engines.

### Model Size

The aggregate size of models (acoustic and language), in MB. We omit this metric for cloud-based engines.

## Speech-to-Text Engines

### Amazon Transcribe

Amazon Transcribe is a cloud-based speceh recognition engine, offered by AWS. Find more information [here](https://aws.amazon.com/transcribe/).

### CMU PocketSphinx

[PocketSphinx](https://github.com/cmusphinx/pocketsphinx) works offline and can run on embedded platforms such as
Raspberry Pi.

### Google Speech-to-Text

A cloud-based speech recognition engine offered by Google Cloud Platform. Find more information
[here](https://cloud.google.com/speech-to-text/).

### Mozilla DeepSpeech

[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open-source implementation of
[Baidu's DeepSpeech](https://arxiv.org/abs/1412.5567) by Mozilla.

### Picovoice Cheetah

[Cheetah](https://github.com/Picovoice/cheetah) is a speech-to-text engine developed using
[Picovoice's](http://picovoice.ai/) proprietary deep learning technology. It works offline and is supported on a
growing number of mobile/embedded platforms including Android, iOS, and Raspberry Pi.

## Usage

Below is information on how to use this framework to benchmark the speech-to-text engines. 

1. Make sure that you have installed DeepSpeech and PocketSphinx on your machine by following the instructions on their official pages.
1. Unpack
DeepSpeech's models under [resources/deepspeech](/resources/deepspeech).
1. Download the [test-clean](http://www.openslr.org/resources/12/test-clean.tar.gz) portion of LibriSpeech and unpack it under
[resources/data](/resources/data).
1. For running Google Speech-to-Text and Amazon Transcribe, you need to sign up for the respective cloud provider
and setup permissions / credentials according to their documentation. Running these services may incur fees.

### Word Error Rate Measurement

Word Error Rate can be measured by running the following command from the root of the repository: 

```bash
python benchmark.py --engine_type AN_ENGINE_TYPE
```

The valid options for the `engine_type`
parameter are: `AMAZON_TRANSCRIBE`, `CMU_POCKET_SPHINX`, `GOOGLE_SPEECH_TO_TEXT`, `MOZILLA_DEEP_SPEECH`,
`PICOVOICE_CHEETAH`, and `PICOVOICE_CHEETAH_LIBRISPEECH_LM`.

`PICOVOICE_CHEETAH_LIBRISPEECH_LM` is the same as `PICOVOICE_CHEETAH`
except that the language model is trained on LibriSpeech training text similar to
[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech/tree/master/data/lm).


### Real Time Factor Measurement

The `time` command is used to measure the execution time of different engines for a given audio file, and then divide
the CPU time by audio length. To measure the execution time for Cheetah, run:

```bash
time resources/cheetah/cheetah_demo \
resources/cheetah/libpv_cheetah.so \
resources/cheetah/acoustic_model.pv \
resources/cheetah/language_model.pv \
resources/cheetah/cheetah_eval_linux.lic \
PATH_TO_WAV_FILE
```

The output should have the following format (values may be different):

```bash
real	0m4.961s
user	0m4.936s
sys	0m0.024s
```

Then, divide the `user` value by the length of the audio file, in seconds. The user value is the actual CPU time spent in the program.

For DeepSpeech:

```bash
time deepspeech \
--model resources/deepspeech/output_graph.pbmm \
--alphabet resources/deepspeech/alphabet.txt \
--lm resources/deepspeech/lm.binary \
--trie resources/deepspeech/trie \
--audio PATH_TO_WAV_FILE
```

Finally, for PocketSphinx:

```bash
time pocketsphinx_continuous -infile PATH_TO_WAV_FILE
```

## Results

The below results are obtained by following the previous steps. The benchmarking was performed on a Linux machine running
Ubuntu 16.04 with 64GB of RAM and an Intel i5-6500 CPU running at 3.2 GHz. WER refers to word error rate and RTF refers to
real time factor.

| Engine | WER (test-clean) | RTF (Desktop) | RTF (Raspberry Pi 3) | RTF (Raspberry Pi Zero) | Model Size (Acoustic and Language) |
:---:|:---:|:---:|:---:|:---:|:---:
Amazon Transcribe | **8.21%** | N/A | N/A | N/A | N/A |
CMU PocketSphinx (0.1.15) | 31.82% | 0.32 | 1.87 | 2.04 | 97.8 MB |
Google Speech-to-Text | 12.23% | N/A | N/A | N/A | N/A |
Mozilla DeepSpeech (0.5.1) | 8.3% | 0.46  | N/A | N/A | 2010.5 MB |
Picovoice Cheetah (v1.1.0) | 13.25% | **0.02** | **0.22** | **1.69** | 46.6 MB |
Picovoice Cheetah LibriSpeech LM (v1.1.0) | 10.47% | **0.02** | **0.22** | **1.69** | **38.2 MB** |

The figure below compares the word error rate of speech-to-text engines. For Picovoice, we included the engine that was
trained on LibriSpeech training data similar to Mozilla DeepSpeech.

![](resources/doc/word_error_rate_comparison.png)

The figure below compares accuracy and runtime metrics of offline speech-to-text engines. For Picovoice we included the engine that was
trained on LibriSpeech training data similar to Mozilla DeepSpeech. Cheetah achieves a performance close to the most accurate
engine (Mozilla DeepSpeech) while being 23X faster and 53X smaller in size.

![](resources/doc/offline_stt_comparison.png)

## License

The benchmarking framework is freely available and can be used under the Apache 2.0 license. Regarding Mozilla DeepSpeech
and PocketSphinx usage, please refer to their respective documentation.

The provided Cheetah resources (binary, model, and license file) are the property of Picovoice. They are
only to be used for evaluation purposes and their use in any commercial product is strictly prohibited.

For commercial enquiries regarding Cheetah, please contact us via this [form](https://picovoice.ai/contact.html).
