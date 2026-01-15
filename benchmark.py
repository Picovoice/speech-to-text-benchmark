import math
import os
import random
from argparse import ArgumentParser
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from typing import (
    Any,
    Dict,
    Sequence
)

from dataset import (
    Dataset,
    Datasets
)
from engine import (
    Engine,
    Engines,
    StreamingEngines
)
from languages import Languages
from metric import (
    Metric,
    Metrics
)
from normalizer import (
    SUPPORTED_PUNCTUATION_SET,
    EnglishNormalizer,
    Normalizer
)

WorkerResult = namedtuple("WorkerResult", ["metric", "num_errors", "num_tokens", "audio_sec", "process_sec"])
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results")


def process(
    engine_name: Engines,
    engine_params: Dict[str, Any],
    language: Languages,
    punctuation: bool,
    punctuation_set: str,
    dataset_name: Datasets,
    dataset_folder: str,
    indices: Sequence[int],
    metric_names: Sequence[Metrics],
) -> Sequence[WorkerResult]:
    engine: Engine = Engine.create(engine_name, language=language, **engine_params)
    dataset: Dataset = Dataset.create(
        dataset_name,
        folder=dataset_folder,
        language=language,
        punctuation=punctuation,
        punctuation_set=punctuation_set,
    )
    normalizer = Normalizer.create(language=language, keep_punctuation=punctuation, punctuation_set=punctuation_set)

    metrics = {m: Metric.create(m) for m in metric_names}
    results = {m: {"num_errors": 0, "num_tokens": 0} for m in metric_names}

    for index in indices:
        audio_path, ref_transcript = dataset.get(index)

        transcript = engine.transcribe(audio_path)
        norm_transcript = normalizer.normalize(transcript)

        ref_sentence = ref_transcript.strip("\n ").lower()
        transcribed_sentence = norm_transcript.strip("\n ").lower()

        if language == Languages.EN:
            ref_sentence = EnglishNormalizer.to_american(EnglishNormalizer.normalize_abbreviations(ref_sentence))
            transcribed_sentence = EnglishNormalizer.to_american(
                EnglishNormalizer.normalize_abbreviations(transcribed_sentence)
            )

        for metric_name, metric in metrics.items():
            num_errors, num_tokens = metric.calculate(prediction=transcribed_sentence, reference=ref_sentence)
            results[metric_name]["num_errors"] += num_errors
            results[metric_name]["num_tokens"] += num_tokens

    engine.delete()

    worker_results = []
    for metric_name in metric_names:
        worker_results.append(
            WorkerResult(
                metric=metric_name.value,
                num_errors=results[metric_name]["num_errors"],
                num_tokens=results[metric_name]["num_tokens"],
                audio_sec=engine.audio_sec(),
                process_sec=engine.process_sec(),
            )
        )

    return worker_results


def main():
    parser = ArgumentParser()
    parser.add_argument("--engine", required=True, choices=[x.value for x in Engines])
    parser.add_argument("--dataset", required=True, choices=[x.value for x in Datasets])
    parser.add_argument("--dataset-folder", required=True)
    parser.add_argument("--language", required=True, choices=[x.value for x in Languages])
    parser.add_argument("--punctuation", action="store_true")
    parser.add_argument("--punctuation-set", type=str, default=".?")
    parser.add_argument("--streaming-chunk-size-ms", type=int, default=32)
    parser.add_argument("--aws-profile")
    parser.add_argument("--aws-location")
    parser.add_argument("--azure-speech-key")
    parser.add_argument("--azure-speech-location")
    parser.add_argument("--google-application-credentials")
    parser.add_argument("--picovoice-access-key")
    parser.add_argument("--picovoice-model-path", default=None)
    parser.add_argument("--picovoice-library-path", default=None)
    parser.add_argument("--watson-speech-to-text-api-key")
    parser.add_argument("--watson-speech-to-text-url")
    parser.add_argument("--num-examples", type=int, default=None)
    parser.add_argument("--num-workers", type=int, default=os.cpu_count())
    parser.add_argument("--pv-device", default="cpu:1")
    args = parser.parse_args()

    engine_name = Engines(args.engine)
    dataset_name = Datasets(args.dataset)
    language = Languages(args.language)
    punctuation = args.punctuation
    punctuation_set = args.punctuation_set
    dataset_folder = args.dataset_folder
    num_examples = args.num_examples
    num_workers = args.num_workers

    engine_params = dict()
    if engine_name in [Engines.AMAZON_TRANSCRIBE, Engines.AMAZON_TRANSCRIBE_STREAMING]:
        if args.aws_profile is None or args.aws_location is None:
            raise ValueError("`aws-profile` and `aws-location` is required")
        os.environ["AWS_PROFILE"] = args.aws_profile
    elif engine_name in [Engines.AZURE_SPEECH_TO_TEXT, Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME]:
        if args.azure_speech_key is None or args.azure_speech_location is None:
            raise ValueError("`azure-speech-key` and `azure-speech-location` are required")
        engine_params["azure_speech_key"] = args.azure_speech_key
        engine_params["azure_speech_location"] = args.azure_speech_location
    elif engine_name in [
        Engines.GOOGLE_SPEECH_TO_TEXT,
        Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED,
        Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING,
        Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING,
    ]:
        if args.google_application_credentials is None:
            raise ValueError("`google-application-credentials` is required")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.google_application_credentials
    elif engine_name in [Engines.PICOVOICE_CHEETAH, Engines.PICOVOICE_CHEETAH_FAST]:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN.value:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["device"] = args.pv_device
        engine_params["library_path"] = args.picovoice_library_path
        engine_params["punctuation"] = punctuation
    elif engine_name == Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN.value:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["device"] = args.pv_device
        engine_params["library_path"] = args.picovoice_library_path
        engine_params["punctuation"] = punctuation
    elif engine_name == Engines.IBM_WATSON_SPEECH_TO_TEXT:
        if args.watson_speech_to_text_api_key is None or args.watson_speech_to_text_url is None:
            raise ValueError("`watson-speech-to-text-api-key` and `watson-speech-to-text-url` are required")
        engine_params["watson_speech_to_text_api_key"] = args.watson_speech_to_text_api_key
        engine_params["watson_speech_to_text_url"] = args.watson_speech_to_text_url

    if engine_name in StreamingEngines and engine_name not in [Engines.PICOVOICE_CHEETAH, Engines.PICOVOICE_CHEETAH_FAST]:
        engine_params["chunk_size_ms"] = args.streaming_chunk_size_ms
        engine_params["apply_delay"] = False
        engine_params["ignore_punctuation"] = False

    for p in punctuation_set:
        if p not in SUPPORTED_PUNCTUATION_SET:
            raise ValueError(f"`{p}` is not a supported punctuation character")

    dataset = Dataset.create(
        dataset_name,
        folder=dataset_folder,
        language=language,
        punctuation=punctuation,
        punctuation_set=punctuation_set,
    )
    indices = list(range(dataset.size()))
    random.shuffle(indices)
    if args.num_examples is not None:
        indices = indices[:num_examples]

    chunk = math.ceil(len(indices) / num_workers)

    metrics = [Metrics.PER] if punctuation else [Metrics.WER]

    print(f"Processing {len(indices)} examples...")
    futures = []
    with ProcessPoolExecutor(num_workers) as executor:
        for i in range(num_workers):
            future = executor.submit(
                process,
                engine_name=engine_name,
                engine_params=engine_params,
                language=language,
                punctuation=punctuation,
                punctuation_set=punctuation_set,
                dataset_name=dataset_name,
                dataset_folder=dataset_folder,
                indices=indices[i * chunk : (i + 1) * chunk],
                metric_names=metrics,
            )
            futures.append(future)

    results = []
    for future in futures:
        results.extend(future.result())

    metric_results = {}
    for result in results:
        if result.metric not in metric_results:
            metric_results[result.metric] = []
        metric_results[result.metric].append(result)

    rtf = sum(x.process_sec for x in results) / sum(x.audio_sec for x in results)

    results_log_path = os.path.join(RESULTS_FOLDER, language.value, dataset_name.value, f"{str(engine_name)}.log")
    os.makedirs(os.path.dirname(results_log_path), exist_ok=True)
    with open(results_log_path, "w") as f:
        for metric_name, metric_results in metric_results.items():
            num_errors = sum(x.num_errors for x in metric_results)
            num_tokens = sum(x.num_tokens for x in metric_results)
            error_rate = 100 * float(num_errors) / num_tokens

            f.write(f"{metric_name}: {str(error_rate)}\n")
            print(f"{metric_name}: {error_rate:.2f}")

        f.write(f"RTF: {str(rtf)}\n")
        print(f"RTF: {rtf}")


if __name__ == "__main__":
    main()
