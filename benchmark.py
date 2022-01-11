import os
from argparse import ArgumentParser

import editdistance

from dataset import *
from engine import *


def main():
    parser = ArgumentParser()
    parser.add_argument('--engine', required=True, choices=[x.value for x in Engines])
    parser.add_argument('--dataset', required=True, choices=[x.value for x in Datasets])
    parser.add_argument('--dataset-folder', required=True)
    parser.add_argument('--aws-profile')
    parser.add_argument('--google-application-credentials')
    parser.add_argument('--deepspeech-pbmm')
    parser.add_argument('--deepspeech-scorer')
    parser.add_argument('--picovoice-access-key')
    parser.add_argument('--num-examples', type=int, default=None)
    args = parser.parse_args()

    args.engine = Engines[args.engine]

    dataset = Dataset.create(Datasets.LIBRI_SPEECH, folder=args.dataset_folder)
    print(f'Loaded {dataset} with {dataset.size()} utterances')

    kwargs = dict()
    if args.engine is Engines.AMAZON_TRANSCRIBE:
        if args.aws_profile is None:
            raise ValueError("`aws_profile` is required")
        os.environ['AWS_PROFILE'] = args.aws_profile
    elif args.engine == Engines.GOOGLE_SPEECH_TO_TEXT:
        if args.google_application_credentials is None:
            raise ValueError("`google_application_credentials` is required")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.google_application_credentials
    elif args.engine == Engines.MOZILLA_DEEP_SPEECH:
        if args.deepspeech_pbmm is None or args.deepspeech_scorer is None:
            raise ValueError("`deepspeech_pbmm` and `deepspeech_scorer` are required")
        kwargs['pbmm_path'] = args.deepspeech_pbmm
        kwargs['scorer_path'] = args.deepspeech_scorer
    elif args.engine == Engines.PICOVOICE_CHEETAH:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice_access_key` is required")
        kwargs['access_key'] = args.picovoice_access_key
    elif args.engine == Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice_access_key` is required")
        kwargs['access_key'] = args.picovoice_access_key

    engine = Engine.create(args.engine, **kwargs)
    print(f'Created {engine} engine')

    error_count = 0
    word_count = 0
    for i in range(dataset.size() if args.num_examples is None else min(dataset.size(), args.num_examples)):
        audio_path, ref_transcript = dataset.get(i)

        transcript = engine.transcribe(audio_path)

        ref_words = ref_transcript.strip('\n ').lower().split()
        words = transcript.strip('\n ').lower().split()

        error_count += editdistance.eval(ref_words, words)
        word_count += len(ref_words)

    print(f'WER: {(100 * float(error_count) / word_count):.2f}')
    print(f'RTF: {engine.rtf()} sec')


if __name__ == '__main__':
    main()
