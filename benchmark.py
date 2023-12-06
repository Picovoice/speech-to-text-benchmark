import math
import os
import random
from argparse import ArgumentParser
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from typing import *

import editdistance

from dataset import *
from engine import *

WorkerResult = namedtuple('WorkerResult', ['num_errors', 'num_words', 'rtf'])


def process(
        engine: Engines,
        engine_params: Dict[str, Any],
        dataset: Datasets,
        dataset_folder: str,
        indices: Sequence[int]) -> WorkerResult:
    engine = Engine.create(engine, **engine_params)
    dataset = Dataset.create(dataset, folder=dataset_folder)

    error_count = 0
    word_count = 0
    for index in indices:
        audio_path, ref_transcript = dataset.get(index)

        transcript = engine.transcribe(audio_path)

        ref_words = ref_transcript.strip('\n ').lower().split()
        words = transcript.strip('\n ').lower().split()

        error_count += editdistance.eval(ref_words, words)
        word_count += len(ref_words)

    engine.delete()

    return WorkerResult(num_errors=error_count, num_words=word_count, rtf=engine.rtf())


def main():
    parser = ArgumentParser()
    parser.add_argument('--engine', required=True, choices=[x.value for x in Engines])
    parser.add_argument('--dataset', required=True, choices=[x.value for x in Datasets])
    parser.add_argument('--dataset-folder', required=True)
    parser.add_argument('--aws-profile')
    parser.add_argument('--azure-speech-key')
    parser.add_argument('--azure-speech-location')
    parser.add_argument('--google-application-credentials')
    parser.add_argument('--deepspeech-pbmm')
    parser.add_argument('--deepspeech-scorer')
    parser.add_argument('--picovoice-access-key')
    parser.add_argument('--watson-speech-to-text-api-key')
    parser.add_argument('--watson-speech-to-text-url')
    parser.add_argument('--num-examples', type=int, default=None)
    parser.add_argument('--num-workers', type=int, default=os.cpu_count())
    args = parser.parse_args()

    args.engine = Engines[args.engine]

    engine_params = dict()
    if args.engine is Engines.AMAZON_TRANSCRIBE:
        if args.aws_profile is None:
            raise ValueError("`aws-profile` is required")
        os.environ['AWS_PROFILE'] = args.aws_profile
    elif args.engine is Engines.AZURE_SPEECH_TO_TEXT:
        if args.azure_speech_key is None or args.azure_speech_location is None:
            raise ValueError("`azure-speech-key` and `azure-speech-location` are required")
        engine_params['azure_speech_key'] = args.azure_speech_key
        engine_params['azure_speech_location'] = args.azure_speech_location
    elif args.engine is Engines.GOOGLE_SPEECH_TO_TEXT or args.engine == Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED:
        if args.google_application_credentials is None:
            raise ValueError("`google-application-credentials` is required")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.google_application_credentials
    elif args.engine is Engines.PICOVOICE_CHEETAH:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        engine_params['access_key'] = args.picovoice_access_key
    elif args.engine is Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        engine_params['access_key'] = args.picovoice_access_key
    elif args.engine is Engines.IBM_WATSON_SPEECH_TO_TEXT:
        if args.watson_speech_to_text_api_key is None or args.watson_speech_to_text_url is None:
            raise ValueError("`watson-speech-to-text-api-key` and `watson-speech-to-text-url` are required")
        engine_params['watson_speech_to_text_api_key'] = args.watson_speech_to_text_api_key
        engine_params['watson_speech_to_text_url'] = args.watson_speech_to_text_url

    args.dataset = Datasets[args.dataset]
    dataset = Dataset.create(args.dataset, folder=args.dataset_folder)

    indices = list(range(dataset.size()))
    random.shuffle(indices)
    if args.num_examples is not None:
        indices = indices[:args.num_examples]

    num_workers = args.num_workers
    chunk = math.ceil(len(indices) / num_workers)

    # res = process(
    #     engine=args.engine,
    #     engine_params=engine_params,
    #     dataset=args.dataset,
    #     dataset_folder=args.dataset_folder,
    #     indices=indices[0:10],
    # )
    # import code
    # code.interact(local=locals())
    # return

    futures = list()
    with ProcessPoolExecutor(num_workers) as executor:
        for i in range(num_workers):
            future = executor.submit(
                process,
                engine=args.engine,
                engine_params=engine_params,
                dataset=args.dataset,
                dataset_folder=args.dataset_folder,
                indices=indices[i * chunk: (i + 1) * chunk]
            )
            futures.append(future)

    res = [x.result() for x in futures]

    num_errors = sum(x.num_errors for x in res)
    num_words = sum(x.num_words for x in res)
    rtf = sum(x.rtf for x in res) / len(res)

    print(f'WER: {(100 * float(num_errors) / num_words):.2f}')
    print(f'RTF: {rtf}')


if __name__ == '__main__':
    main()
