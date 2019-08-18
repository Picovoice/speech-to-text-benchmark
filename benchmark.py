import argparse
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

import editdistance

from dataset import *
from engine import *

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)


def _word_error_info(ref, decoded):
    """
    Computes the number of errors for a given decoded transcription and the number of words in reference transcription.

    :param ref: Reference (true) transcription.
    :param decoded: Decoded (by speech-to-text engine) transcription.
    :return: Tuple of number of word errors and number of words in reference transcription.
    """

    ref_words = ref.strip('\n ').lower().split()
    decoded_words = decoded.strip('\n ').lower().split()

    word_error_count = editdistance.eval(ref_words, decoded_words)

    return word_error_count, len(ref_words)


def _process_chunk(engine_type, engine_params, data_chunk):
    """
    Transcribes a chuck of data with a given engine and returns number of word errors and total number of words
    processed (number of words in reference transcriptions).

    :param engine_type: Type of speech-to-text engine.
    :param engine_params: Engine parameters.
    :param data_chunk: An array of tuples of path to a WAV file and its corresponding transcription.
    :return: Tuple of total number of word errors and total number of words processed.
    """

    engine = ASREngine.create(engine_type, **engine_params)

    sum_word_error_count = 0
    sum_word_count = 0

    # for path, ref_transcript in data_chunk:
    #     print(engine.transcribe(path))

    futures = list()
    with ThreadPoolExecutor(max_workers=64) as executor:
        for path, ref_transcript in data_chunk:
            futures.append((executor.submit(engine.transcribe, path), ref_transcript))

    results = [_word_error_info(x.result(), y) for (x, y) in futures]
    sum_word_error_count = sum([x[0] for x in results])
    sum_word_count = sum(x[1] for x in results)
    # decoded = engine.transcribe(path)
    # error_count, count = _word_error_info(ref_transcript, decoded)
    # sum_word_error_count += error_count
    # sum_word_count += count

    return sum_word_error_count, sum_word_count


def _run():
    """
    Runs the benchmark. Processes a corpus of speech data with a set of speech-to-text engines and computes their
    average word error rate.
    """

    engines_params = dict([(x, dict()) for x in ASREngines])
    engines_params[ASREngines.AMAZON_TRANSCRIBE].update(dataset_root=args.dataset_root)
    # engines_params[ASREngines.MOZILLA_DEEP_SPEECH].update(
    #     model_path=os.path.expanduser(args.deep_speech_model_path),
    #     alphabet_path=os.path.expanduser(args.deep_speech_alphabet_path),
    #     language_model_path=os.path.expanduser(args.deep_speech_language_model_path),
    #     trie_path=os.path.expanduser(args.deep_speech_trie_path))

    dataset = Dataset.create(args.dataset_type, os.path.expanduser(args.dataset_root))
    logging.info('loaded %s with %f hours of data' % (str(dataset), dataset.size_hours()))

    # NOTE: Depending on how much RAM you have you might need to reduce this when benchmarking DeepSpeech as it consumes
    # lots of RAM (specially when decoding with language model is enabled).
    num_workers = multiprocessing.cpu_count() - 1
    chunk_size = dataset.size() // num_workers

    for engine_type in [ASREngines.AMAZON_TRANSCRIBE]:
        logging.info('evaluating %s' % engine_type.value)

        data_chunk = [dataset.get(j) for j in range(dataset.size())]
        word_error_info = [_process_chunk(engine_type, engines_params[engine_type], data_chunk)]
        # futures = []
        # with ProcessPoolExecutor(num_workers) as pool:
        #     for i in range(num_workers):
        #         data_chunk = [dataset.get(j) for j in range(i * chunk_size, (i + 1) * chunk_size)]
        #         future = pool.submit(
        #             _process_chunk,
        #             engine_type,
        #             engines_params[engine_type],
        #             data_chunk)
        #         futures.append(future)
        #
        # word_error_info = [x.result() for x in futures]
        word_error_count = sum([x[0] for x in word_error_info])
        word_count = sum([x[1] for x in word_error_info])

        logging.info('WER = %f' % (float(word_error_count) / word_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_type', type=str, required=True)
    parser.add_argument('--dataset_root', type=str, required=True)
    # parser.add_argument('--deep_speech_model_path', type=str, required=True)
    # parser.add_argument('--deep_speech_alphabet_path', type=str, required=True)
    # parser.add_argument('--deep_speech_language_model_path', type=str, required=True)
    # parser.add_argument('--deep_speech_trie_path', type=str, required=True)

    args = parser.parse_args()

    _run()
