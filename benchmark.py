from argparse import ArgumentParser

import editdistance

from dataset import *
from engine import *


def main():
    parser = ArgumentParser()
    parser.add_argument('--engine', required=True, choices=[x.value for x in Engines])
    args = parser.parse_args()

    dataset = Dataset.create(Datasets.LIBRI_SPEECH)

    engine = Engine.create(Engines[args.engine_type])
    print('created %s engine' % str(engine))

    word_error_count = 0
    word_count = 0
    for i in range(dataset.size()):
        path, ref_transcript = dataset.get(i)

        transcript = engine.transcribe(path)

        ref_words = ref_transcript.strip('\n ').lower().split()
        words = transcript.strip('\n ').lower().split()

        word_error_count += editdistance.eval(ref_words, words)
        word_count += len(ref_words)

    print('word error rate : %.2f' % (100 * float(word_error_count) / word_count))


if __name__ == '__main__':
    main()
