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
from languages import Languages
from normalizer import EnglishNormalizer

WorkerResult = namedtuple(
    "WorkerResult", ["num_errors", "num_words", "audio_sec", "process_sec"]
)
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results")


def process(
    engine: Engines,
    engine_params: Dict[str, Any],
    language: Languages,
    dataset: Datasets,
    dataset_folder: str,
    indices: Sequence[int],
) -> WorkerResult:
    engine = Engine.create(engine, language=language, **engine_params)
    dataset = Dataset.create(dataset, folder=dataset_folder, language=language)

    error_count = 0
    word_count = 0
    for index in indices:
        audio_path, ref_transcript = dataset.get(index)

        transcript = engine.transcribe(audio_path)

        ref_sentence = ref_transcript.strip("\n ").lower()
        transcribed_sentence = transcript.strip("\n ").lower()

        if language == Languages.EN:
            ref_words = EnglishNormalizer.to_american(
                EnglishNormalizer.normalize_abbreviations(ref_sentence)
            ).split()
            transcribed_words = EnglishNormalizer.to_american(
                EnglishNormalizer.normalize_abbreviations(transcribed_sentence)
            ).split()
        else:
            ref_words = ref_sentence.split()
            transcribed_words = transcribed_sentence.split()

        error_count += editdistance.eval(ref_words, transcribed_words)
        word_count += len(ref_words)

    engine.delete()

    return WorkerResult(
        num_errors=error_count,
        num_words=word_count,
        audio_sec=engine.audio_sec(),
        process_sec=engine.process_sec(),
    )


def main():
    parser = ArgumentParser()
    parser.add_argument("--engine", required=True, choices=[x.value for x in Engines])
    parser.add_argument("--dataset", required=True, choices=[x.value for x in Datasets])
    parser.add_argument("--dataset-folder", required=True)
    parser.add_argument(
        "--language", required=True, choices=[x.value for x in Languages]
    )
    parser.add_argument("--aws-profile")
    parser.add_argument("--azure-speech-key")
    parser.add_argument("--azure-speech-location")
    parser.add_argument("--google-application-credentials")
    parser.add_argument("--deepspeech-pbmm")
    parser.add_argument("--deepspeech-scorer")
    parser.add_argument("--picovoice-access-key")
    parser.add_argument("--picovoice-model-path", default=None)
    parser.add_argument("--picovoice-library-path", default=None)
    parser.add_argument("--watson-speech-to-text-api-key")
    parser.add_argument("--watson-speech-to-text-url")
    parser.add_argument("--num-examples", type=int, default=None)
    parser.add_argument("--num-workers", type=int, default=os.cpu_count())
    args = parser.parse_args()

    engine = Engines(args.engine)
    dataset_type = Datasets(args.dataset)
    language = Languages(args.language)
    dataset_folder = args.dataset_folder
    num_examples = args.num_examples
    num_workers = args.num_workers

    engine_params = dict()
    if engine == Engines.AMAZON_TRANSCRIBE:
        if args.aws_profile is None:
            raise ValueError("`aws-profile` is required")
        os.environ["AWS_PROFILE"] = args.aws_profile
    elif engine == Engines.AZURE_SPEECH_TO_TEXT:
        if args.azure_speech_key is None or args.azure_speech_location is None:
            raise ValueError(
                "`azure-speech-key` and `azure-speech-location` are required"
            )
        engine_params["azure_speech_key"] = args.azure_speech_key
        engine_params["azure_speech_location"] = args.azure_speech_location
    elif (
        engine == Engines.GOOGLE_SPEECH_TO_TEXT
        or engine == Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED
    ):
        if args.google_application_credentials is None:
            raise ValueError("`google-application-credentials` is required")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            args.google_application_credentials
        )
    elif engine == Engines.PICOVOICE_CHEETAH:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["library_path"] = args.picovoice_library_path
    elif engine == Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["library_path"] = args.picovoice_library_path
    elif engine == Engines.IBM_WATSON_SPEECH_TO_TEXT:
        if (
            args.watson_speech_to_text_api_key is None
            or args.watson_speech_to_text_url is None
        ):
            raise ValueError(
                "`watson-speech-to-text-api-key` and `watson-speech-to-text-url` are required"
            )
        engine_params["watson_speech_to_text_api_key"] = (
            args.watson_speech_to_text_api_key
        )
        engine_params["watson_speech_to_text_url"] = args.watson_speech_to_text_url

    dataset = Dataset.create(dataset_type, folder=dataset_folder, language=language)
    indices = list(range(dataset.size()))
    random.shuffle(indices)
    if args.num_examples is not None:
        indices = indices[:num_examples]

    chunk = math.ceil(len(indices) / num_workers)

    print(f"Processing {len(indices)} examples...")

    futures = []
    with ProcessPoolExecutor(num_workers) as executor:
        for i in range(num_workers):
            future = executor.submit(
                process,
                engine=engine,
                engine_params=engine_params,
                language=language,
                dataset=dataset_type,
                dataset_folder=dataset_folder,
                indices=indices[i * chunk : (i + 1) * chunk],
            )
            futures.append(future)

    res = [x.result() for x in futures]

    num_errors = sum(x.num_errors for x in res)
    num_words = sum(x.num_words for x in res)

    rtf = sum(x.process_sec for x in res) / sum(x.audio_sec for x in res)
    word_error_rate = 100 * float(num_errors) / num_words

    results_log_path = os.path.join(
        RESULTS_FOLDER, language.value, dataset_type.value, f"{str(engine)}.log"
    )
    os.makedirs(os.path.dirname(results_log_path), exist_ok=True)
    with open(results_log_path, "w") as f:
        f.write(f"WER: {str(word_error_rate)}\n")
        f.write(f"RTF: {str(rtf)}\n")

    print(f"WED: {word_error_rate:.2f}")
    print(f"RTF: {rtf}")


if __name__ == "__main__":
    main()
