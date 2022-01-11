from argparse import ArgumentParser

import editdistance

from dataset import *
from engine import *


def main():
    parser = ArgumentParser()
    parser.add_argument('--engine', required=True, choices=[x.value for x in Engines])
    parser.add_argument('--dataset', required=True, choices=[x.value for x in Datasets])
    parser.add_argument('--dataset-folder', required=True)
    parser.add_argument('--picovoice-access-key')
    parser.add_argument('--deepspeech-pbmm')
    parser.add_argument('--deepspeech-scorer')
    parser.add_argument('--num-examples', type=int, default=None)
    args = parser.parse_args()

    args.engine = Engines[args.engine]

    dataset = Dataset.create(Datasets.LIBRI_SPEECH, folder=args.dataset_folder)
    print(f'loaded {dataset} with {dataset.size()} utterances')

    if args.engine == Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError()
        engine = Engine.create(args.engine, access_key=args.picovoice_access_key)
    elif args.engine == Engines.MOZILLA_DEEP_SPEECH:
        if args.deepspeech_pbmm is None or args.deepspeech_scorer is None:
            raise ValueError()
        engine = Engine.create(args.engine, pbmm_path=args.deepspeech_pbmm, scorer_path=args.deepspeech_scorer)
    else:
        raise ValueError()
    print(f'created `{engine}` engine')

    word_error_count = 0
    word_count = 0
    for i in range(dataset.size() if args.num_examples is None else min(dataset.size(), args.num_examples)):
        audio_path, ref_transcript = dataset.get(i)

        transcript = engine.transcribe(audio_path)

        ref_words = ref_transcript.strip('\n ').lower().split()
        words = transcript.strip('\n ').lower().split()

        word_error_count += editdistance.eval(ref_words, words)
        word_count += len(ref_words)

    print(f'WER : {(100 * float(word_error_count) / word_count):.2f}')
    print(f'proc took {engine.proc_sec()} sec')


if __name__ == '__main__':
    main()
