# Speech-to-Text Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This is a minimalist and extensible framework for benchmarking different speech-to-text engines. It has been developed
and tested on Ubuntu with Python3.

## Table of Contents

* [Background](#background)
* [Data](#data)
* [Metrics](#metrics)
    * [Word Error Rate](#word-error-rate)
    * [Real Time Factor](#real-time-factor)
    * [Model Size (Acoustic & Language)](#model-size)
* [Speech-to-Text Engines](#speech-to-text-engines)
    * [Amazon Transcribe](#amazon-transcribe)
    * [Google Speech-to-Text](#google-speech-to-text)
    * [Mozilla DeepSpeech](#mozilla-deepspeech)
    * [Picovoice Cheetah](#picovoice-cheetah)
    * [PocketSphinx](#pocketsphinx)
* [Usage](#usage)
    * [Word Error Rate Measurement](#word-error-rate-measurement)
    * [Real Time Factor Measurement](#real-time-factor-measurement)
    * [Memory Usage Measurement](#memory-usage-measurement)
* [Results](#results)
* [License](#license)

## Background

This framework has been developed by [Picovoice](http://picovoice.ai/) as part of the project
[Cheetah](https://github.com/Picovoice/cheetah). Cheetah is Picovoice's speech-to-text engine specifically designed to
run efficiently on the edge (offline). Deep learning has been the main driver in recent improvements in speech recognition.
But due to stringent compute/storage limitations of IoT platforms it is most beneficial to the cloud-based engines. Picovoice's
proprietary deep learning technology enables transferring these improvements to IoT platforms with much lower CPU/memory
footprint. The goal is to be able to run Cheetah on any platform with a C Compiler and a few MB of memory.

## Data

[LibriSpeech](http://www.openslr.org/12/) dataset is used for benchmarking. We use the
[test-clean](http://www.openslr.org/resources/12/test-clean.tar.gz) portion of LibriSpeech dataset to allow engines use
the train portions.

## Metrics

Three different metrics are measured.

### Word Error Rate

Word error rate is defined as the [Levenstein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
between words in reference transcript and words in the output of the speech-to-text engine to the number of
words in reference transcript.

### Real Time Factor

Real-time factor (RTF) is measured as the ratio of CPU (processing) time in seconds to the length
of the input speech file in seconds. A speech-to-text engine with lower RTF is computationally more efficient. We omit
this metric for cloud-based engines.

### Model Size

The aggregate size of models in MB (accoustic and language model). This metrics indicates the amount of memory (RAM and ROM)
needed to run the engine.

## Speech-to-Text Engines

### Amazon Transcribe

Find more information [here](https://aws.amazon.com/transcribe/).

### Google Speech-to-Text

Find more information [here](https://cloud.google.com/speech-to-text/).

### Mozilla DeepSpeech

[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open-source implementation of
[Baidu's DeepSpeech](https://arxiv.org/abs/1412.5567) by Mozilla.

### Picovoice Cheetah

[Cheetah](https://github.com/Picovoice/cheetah) is a speech-to-text engine developed using
[Picovoice's](http://picovoice.ai/) proprietary deep learning technology. It works offline and is supported on a
growing number of mobile/embedded platforms including Android, iOS, and Raspberry Pi.

### PocketSphinx

[PocketSphinx](https://github.com/cmusphinx/pocketsphinx) works offline and can run on embedded platforms such as
Raspberry Pi.

## Usage

Below is information on how to use this framework to benchmark engines mentioned above. First, make sure that you have
already installed DeepSpeech and PocketSphinx on your machine following instructions on their official pages. Then unpack
DeepSpeech's models under [resources/deepspeech](/resources/deepspeech).

Then download [test-clean](http://www.openslr.org/resources/12/test-clean.tar.gz) portion of LibriSpeech and unpack it under
[resources/data](/resources/data).

For running Google Speech-to-Text and Amazon Transcribe engines you need to sign up for the respective cloud provider
and setup permissions / credentials according to their documentation. Running these services might incur fees. 

### Word Error Rate Measurement

WER can be measured by running the following command from the root of the repository. The valid options for `engine_type` parameter
are `AMAZON_TRANSCRIBE`, `GOOGLE_SPEECH_TO_TEXT`, `MOZILLA_DEEP_SPEECH`, `PICOVOICE_CHEETAH`, `PICOVOICE_CHEETAH_LIBRISPEECH_LM`, and `CMU_POCKET_SPHINX`.


```bash
python benchmark.py --engine_type MOZILLA_DEEP_SPEECH
```

The above prints the WER for `MOZILLA_DEEP_SPEECH` in console.

### Real Time Factor Measurement

`time` command is used to measure execution time of different engines for a given audio file and then divide
the CPU time by audio length. In order to measure execution time for Cheetah run

```bash
time resources/cheetah/cheetah_demo resources/cheetah/libpv_cheetah.so resources/cheetah/acoustic_model.pv \
resources/cheetah/language_model.pv resources/cheetah/cheetah_eval_linux.lic PATH_TO_WAV_FILE
```

The output should have the following format (values will be different)

```bash
real	0m4.961s
user	0m4.936s
sys	0m0.024s
```

then divide `user` by length of the audio file in seconds. The user is the actual CPU time spent in the program.

For DeepSpeech

```bash
time deepspeech --model DEEP_SPEECH_MODELS_PATH/output_graph.pbmm --alphabet PATH_TO_WAV_FILE DEEP_SPEECH_MODELS_PATH/alphabet.txt \
--lm DEEP_SPEECH_MODELS_PATH/lm.binary --trie DEEP_SPEECH_MODELS_PATH/trie --audio PATH_TO_WAV_FILE
```

Finally, for PocketSphinx

```bash
time pocketsphinx_continuous -infile PATH_TO_WAV_FILE
```

## Results

Below results are obtained by following the steps above. The benchmarking is performed on a linux box running
Ubuntu 16.04 with 64 GB of RAM and Intel i5-6500 CPU running at 3.2 GHz. WER refers to word error rate and RTF refers to
real time factor.

| Engine | WER (test-clean) | RTF (Desktop) | RTF (Raspberry Pi 3) | RTF (Raspberry Pi Zero) | Model Size (Acoustic and Language) |
:---:|:---:|:---:|:---:|:---:|:---:
Amazon Transcribe | 8.21% | N/A | N/A | N/A | N/A |
Google Speech-to-Text | 12.23% | N/A | N/A | N/A | N/A |
Mozilla DeepSpeech (0.5.1) | 8.3% | 0.46  | N/A | N/A | 2010.5 MB |
Picovoice Cheetah (v1.1.0) | 13.28% | 0.02 | 0.22 | 1.69 | 46.6 MB |
Picovoice Cheetah LibriSpeech LM (v1.1.0) | 10.47% | 0.02 | 0.22 | 1.69 | 38.2 MB |
PocketSphinx (0.1.15) | 31.82% | 0.32 | 1.87 | 2.04 | 97.8 MB |

Cheetah achieves higher accuracy compared to any other engine. Compared to second best performing engine,
Mozilla DeepSpeech, it is 7.7 times faster and consumes 28 times less memory storage. This enables Cheetah to run on small
commodity embedded platforms such as Raspberry Pi while delivering the benefits of large models that need much more
compute/memory resources.

## License

The benchmarking framework is freely-available and can be used under the Apache 2.0 license. Regarding Mozilla DeepSpeech
and PocketSphinx please refer to their respective pages.

The provided Cheetah resources (binary, model, and license file) are the property of Picovoice. They are
only to be used for evaluation purposes and their use in any commercial product is strictly prohibited.

For commercial inquiries regarding Cheetah please contact us by filling out this [form](https://picovoice.ai/contact.html).
