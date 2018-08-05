import argparse
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import editdistance

from dataset import *
from engine import *

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)


def _word_error_rate(ref, decoded):
    """
    Computes the word error rate for a given decoded transcription.

    :param ref: Reference (true) transcription.
    :param decoded: Decoded (by speech-to-text engine) transcription.
    :return: Word error rate.
    """

    ref_words = ref.strip('\n ').lower().split()
    decoded_words = decoded.strip('\n ').lower().split()

    error_count = editdistance.eval(ref_words, decoded_words)

    return float(error_count) / len(ref_words)


def _process_chunk(engine_type, engine_params, data_chunk):
    """
    Transcribes a chuck of data with a given engine and returns the average word error rate.

    :param engine_type: Type of speech-to-text engine.
    :param engine_params: Engine parameters.
    :param data_chunk: An array of tuples of path to a WAV file and its corresponding transcription.
    :return: Average word error rate.
    """

    engine = ASREngine.create(engine_type, **engine_params)

    word_error_rates = []
    for path, ref_transcript in data_chunk:
        decoded = engine.transcribe(path)
        word_error_rates.append(_word_error_rate(ref_transcript, decoded))

    return sum(word_error_rates) / len(data_chunk)


def _run():
    """
    Runs the benchmark. Processes a corpus of speech data with a set of speech-to-text engines and computes their
    average word error rate.
    """

    engines_params = dict([(x, dict()) for x in ASREngines])
    engines_params[ASREngines.MOZILLA_DEEP_SPEECH].update(
        model_path=args.deep_speech_model_path,
        alphabet_path=args.deep_speech_alphabet_path,
        language_model_path=args.deep_speech_language_model_path,
        trie_path=args.deep_speech_trie_path)

    dataset = Dataset.create(Datasets.COMMON_VOICE, args.dataset_root)
    logging.info('loaded %s with %f hours of data' % (str(dataset), dataset.size_hours()))

    # NOTE: Depending on how much RAM you have you might need to reduce this when benchmarking DeepSpeech as it consumes
    # lots of RAM (specially when decoding with language model is enabled).
    num_workers = multiprocessing.cpu_count() - 1
    chunk_size = dataset.size() // num_workers

    for engine_type in ASREngines:
        logging.info('evaluating %s' % engine_type.value)

        futures = []
        with ProcessPoolExecutor(num_workers) as pool:
            for i in range(num_workers):
                data_chunk = [dataset.get(j) for j in range(i * chunk_size, (i + 1) * chunk_size)]
                future = pool.submit(
                    _process_chunk,
                    engine_type,
                    engines_params[engine_type],
                    data_chunk)
                futures.append(future)

        word_error_rates = [x.result() for x in futures]

        logging.info('WER = %f' % (sum(word_error_rates) / len(word_error_rates)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_root', type=str, required=True)
    parser.add_argument('--deep_speech_model_path', type=str, required=True)
    parser.add_argument('--deep_speech_alphabet_path', type=str, required=True)
    parser.add_argument('--deep_speech_language_model_path', type=str, default=None, required=False)
    parser.add_argument('--deep_speech_trie_path', type=str, default=None, required=False)

    args = parser.parse_args()

    _run()
