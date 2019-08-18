import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

import editdistance

from dataset import *
from engine import *

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)


def word_error_info(ref, decoded):
    ref_words = ref.strip('\n ').lower().split()
    decoded_words = decoded.strip('\n ').lower().split()

    word_error_count = editdistance.eval(ref_words, decoded_words)

    return word_error_count, len(ref_words)


def run():
    dataset = Dataset.create('librispeech')
    logging.info('loaded %s with %.2f hours of data' % (str(dataset), dataset.size_hours()))

    engine = ASREngine.create(args.engine_type)
    logging.info('created %s engine' % str(engine))

    futures = list()
    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(dataset.size()):
            path, ref_transcript = dataset.get(i)
            futures.append((executor.submit(engine.transcribe, path), ref_transcript))

    results = [word_error_info(x.result(), y) for (x, y) in futures]
    word_error_count = sum([x[0] for x in results])
    word_count = sum(x[1] for x in results)

    logging.info('WER : %.2f' % (100 * float(word_error_count) / word_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine_type', type=str, required=True)
    args = parser.parse_args()

    run()
