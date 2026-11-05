import os
import subprocess
import threading
from argparse import ArgumentParser
from collections.abc import Generator
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Any

import psutil

from engine import (
    Engine,
    Engines,
    StreamingEngines
)
from languages import Languages

RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results", "mem_usage")


def _memory_tree(proc_main):
    total = 0
    proc_list = [proc_main] + proc_main.children(recursive=True)
    for p in proc_list:
        try:
            total += p.memory_full_info().pss
        except psutil.NoSuchProcess:
            pass
    return total


@contextmanager
def measure_peak_memory(interval: float = 0.05) -> Generator[dict[str, float], Any, None]:
    proc_main = psutil.Process()
    peak_mem = 0.
    result = {"peak_mem": peak_mem}
    stop_event = threading.Event()

    initial_mem = _memory_tree(proc_main)

    def _measure():
        nonlocal peak_mem
        while not stop_event.is_set():
            mem = _memory_tree(proc_main)
            peak_mem = max(peak_mem, mem)
            stop_event.wait(interval)

    t = threading.Thread(target=_measure)
    t.start()

    try:
        yield result
    finally:
        stop_event.set()
        t.join()

    result["peak_mem"] = (peak_mem - initial_mem) / (1024**2)


def process(
    engine_name: Engines,
    engine_params: dict[str, Any],
    language: Languages,
    audio_path: str,
) -> float:
    with TemporaryDirectory(prefix="stt-benchmark-memory-") as temp_dir:
        temp_audio_path = os.path.join(temp_dir, "audio.flac")
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-i",
                audio_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                temp_audio_path,
            ],
            check=True,
        )

        with measure_peak_memory() as res:
            engine = Engine.create(engine_name, language=language, **engine_params)
            engine.transcribe(temp_audio_path)

        engine.delete()

    return res["peak_mem"]


def main():
    parser = ArgumentParser()
    parser.add_argument("--engine", required=True, choices=[x.value for x in Engines])
    parser.add_argument("--audio-path", required=True)
    parser.add_argument("--language", required=True, choices=[x.value for x in Languages])
    parser.add_argument("--streaming-chunk-size-ms", type=int, default=None)
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
    args = parser.parse_args()

    engine_name = Engines(args.engine)
    audio_path = args.audio_path
    language = Languages(args.language)

    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"`{audio_path}` does not exist")

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
    elif engine_name is Engines.PICOVOICE_CHEETAH:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN.value:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["library_path"] = args.picovoice_library_path
    elif engine_name is Engines.PICOVOICE_LEOPARD:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN.value:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["library_path"] = args.picovoice_library_path
    elif engine_name is Engines.IBM_WATSON_SPEECH_TO_TEXT:
        if args.watson_speech_to_text_api_key is None or args.watson_speech_to_text_url is None:
            raise ValueError("`watson-speech-to-text-api-key` and `watson-speech-to-text-url` are required")
        engine_params["watson_speech_to_text_api_key"] = args.watson_speech_to_text_api_key
        engine_params["watson_speech_to_text_url"] = args.watson_speech_to_text_url
    if engine_name in StreamingEngines:
        if engine_name not in [Engines.PICOVOICE_CHEETAH]:
            engine_params["chunk_size_ms"] = args.streaming_chunk_size_ms
        if engine_name in [
            Engines.AMAZON_TRANSCRIBE_STREAMING,
            Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME,
            Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING,
            Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING,
        ]:
            engine_params["apply_delay"] = False
            engine_params["ignore_punctuation"] = False

    print("Processing...")

    peak_memory_usage = process(
        engine_name=engine_name, engine_params=engine_params, language=language, audio_path=audio_path
    )

    print(f"Peak memory usage: {peak_memory_usage:.2f}MB")

    results_log_path = os.path.join(RESULTS_FOLDER, language.value, f"{engine_name}.log")
    os.makedirs(os.path.dirname(results_log_path), exist_ok=True)
    with open(results_log_path, "w") as f:
        f.write(f"Peak memory usage: {peak_memory_usage}\n")


if __name__ == "__main__":
    main()
