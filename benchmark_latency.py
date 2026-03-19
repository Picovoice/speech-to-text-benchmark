import json
import math
import os
import random
from argparse import ArgumentParser
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from glob import glob
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple
)

import editdistance
import numpy as np

from engine import (
    Engine,
    Engines,
    StreamingEngine,
    StreamingEngines
)
from languages import Languages

RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results", "latency")

Example = namedtuple("Example", ["transcript", "alignments", "path"])


def load_alignment_data(dataset_folder: str) -> Sequence[Example]:
    examples = []

    json_paths = glob(os.path.join(dataset_folder, "*.json"))
    for json_path in json_paths:
        with open(json_path) as f:
            data = json.load(f)

        examples.append(
            Example(
                transcript=data["transcript"],
                alignments=data["alignments"],
                path=json_path.replace("json", data["format"]),
            )
        )

    return examples


class Aligner:
    @staticmethod
    def _compute_edit_distance_matrix(
        reference_words: Sequence[str], predicted_words: Sequence[str]
    ) -> Sequence[Sequence[int]]:
        m, n = len(reference_words), len(predicted_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if reference_words[i - 1] == predicted_words[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(
                        dp[i - 1][j - 1] + 1,
                        dp[i - 1][j] + 1,
                        dp[i][j - 1] + 1,
                    )

        return dp

    @staticmethod
    def _compute_backpointers(
        dp: Sequence[Sequence[int]], row: int, col: int, ref_words: Sequence[str], pred_words: Sequence[str]
    ) -> Sequence[Tuple[int, int]]:
        if row == 0 and col == 0:
            return []

        backpointers = []

        if row > 0 and col > 0:
            sub_cost = dp[row - 1][col - 1] + (0 if ref_words[row - 1] == pred_words[col - 1] else 1)
            if dp[row][col] == sub_cost:
                backpointers.append((row - 1, col - 1))

        if row > 0:
            del_cost = dp[row - 1][col] + 1
            if dp[row][col] == del_cost:
                backpointers.append((row - 1, col))

        if col > 0:
            ins_cost = dp[row][col - 1] + 1
            if dp[row][col] == ins_cost:
                backpointers.append((row, col - 1))

        return backpointers

    @staticmethod
    def _word_similarity(word1: str, word2: str) -> float:
        return 1.0 - editdistance.eval(word1.lower(), word2.lower())

    def align_words(
        self, ref_words: Sequence[str], pred_words: Sequence[str], max_errors_skip_threshold: int = 20
    ) -> Optional[Sequence[Tuple[str, str]]]:
        dp = self._compute_edit_distance_matrix(ref_words, pred_words)

        if dp[-1][-1] > max_errors_skip_threshold:
            return None

        def backtrack(row: int, col: int) -> Sequence[Tuple[List[Tuple[str, str]], float]]:
            if row == 0 and col == 0:
                return [([], 0.0)]

            backpointers = self._compute_backpointers(dp, row, col, ref_words, pred_words)
            alignments = []

            for prev_i, prev_j in backpointers:
                sub_alignments = backtrack(prev_i, prev_j)
                for sub_alignment, sub_score in sub_alignments:
                    if prev_i == row - 1 and prev_j == col - 1:
                        new_alignment = sub_alignment + [(ref_words[row - 1], pred_words[col - 1])]
                        new_score = sub_score + self._word_similarity(ref_words[row - 1], pred_words[col - 1])
                    elif prev_i == row - 1:
                        new_alignment = sub_alignment + [(ref_words[row - 1], "*")]
                        new_score = sub_score
                    else:
                        new_alignment = sub_alignment + [("*", pred_words[col - 1])]
                        new_score = sub_score

                    alignments.append((new_alignment, new_score))

            return alignments

        all_alignments = backtrack(len(ref_words), len(pred_words))
        best_alignment = max(all_alignments, key=lambda x: x[1])[0]

        return best_alignment

    def align_timings(
        self, ref_timings: Sequence[float], pred_timings: Sequence[float], aligned_words: Sequence[Tuple[str, str]]
    ) -> Sequence[Tuple[float, float]]:
        aligned_timings = []
        ref_idx = 0
        pred_idx = 0
        for ref, pred in aligned_words:
            if ref == "*":
                ref_time = -1
            else:
                ref_time = ref_timings[ref_idx]
                ref_idx += 1

            if pred == "*":
                pred_time = -1
            else:
                pred_time = pred_timings[pred_idx]
                pred_idx += 1

            aligned_timings.append([ref_time, pred_time])

        return aligned_timings


def compute_latencies(
    engine_name: Engines,
    engine_params: Dict[str, Any],
    language: Languages,
    examples: Sequence[Example],
) -> Sequence[float]:
    engine = Engine.create(engine_name, language=language, **engine_params)
    if not isinstance(engine, StreamingEngine):
        raise ValueError(f"`{engine_name}` is not a streaming engine")
    aligner = Aligner()

    latencies = []
    for example in examples:
        audio_path = example.path
        ref_transcript = example.transcript
        alignments = example.alignments

        ref_words = ref_transcript.split()

        transcribed_words, receive_timings, send_timings = engine.measure_word_latency(audio_path, alignments)

        aligned_words = aligner.align_words(ref_words, transcribed_words)
        if aligned_words is not None:
            aligned_timings = aligner.align_timings(send_timings, receive_timings, aligned_words)

            for (send_time, receive_time), (ref_word, transcribed_word) in zip(aligned_timings, aligned_words):
                if ref_word != transcribed_word:
                    continue
                latencies.append(receive_time - send_time)

    return latencies


def main():
    parser = ArgumentParser()
    parser.add_argument("--engine", required=True, choices=[x.value for x in StreamingEngines])
    parser.add_argument("--dataset-folder", required=True)
    parser.add_argument("--language", required=True, choices=[x.value for x in Languages])
    parser.add_argument("--chunk-size-ms", type=int, default=None)
    parser.add_argument("--aws-profile")
    parser.add_argument("--aws-location")
    parser.add_argument("--azure-speech-key")
    parser.add_argument("--azure-speech-location")
    parser.add_argument("--google-application-credentials")
    parser.add_argument("--picovoice-access-key")
    parser.add_argument("--picovoice-model-path")
    parser.add_argument("--picovoice-library-path")
    parser.add_argument("--num-examples", type=int, default=None)
    parser.add_argument("--num-workers", type=int, default=os.cpu_count())
    args = parser.parse_args()

    engine_name = Engines(args.engine)
    language = Languages(args.language)
    dataset_folder = args.dataset_folder
    num_examples = args.num_examples
    num_workers = args.num_workers

    engine_params = dict()
    if engine_name is Engines.AMAZON_TRANSCRIBE_STREAMING:
        if args.aws_location is None or args.aws_profile is None:
            raise ValueError("`aws-location` and `aws-profile` is required")
        os.environ["AWS_PROFILE"] = args.aws_profile
        engine_params["aws_location"] = args.aws_location
        engine_params["apply_delay"] = True
        engine_params["ignore_punctuation"] = True
        engine_params["chunk_size_ms"] = args.chunk_size_ms
    elif engine_name is Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME:
        if args.azure_speech_key is None or args.azure_speech_location is None:
            raise ValueError("`azure-speech-key` and `azure-speech-location` are required")
        engine_params["azure_speech_key"] = args.azure_speech_key
        engine_params["azure_speech_location"] = args.azure_speech_location
        engine_params["chunk_size_ms"] = args.chunk_size_ms
        engine_params["apply_delay"] = True
        engine_params["ignore_punctuation"] = True
    elif engine_name in [Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING, Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING]:
        if args.google_application_credentials is None:
            raise ValueError("`google-application-credentials` is required")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.google_application_credentials
        engine_params["chunk_size_ms"] = args.chunk_size_ms
        engine_params["apply_delay"] = True
        engine_params["ignore_punctuation"] = True
    elif engine_name is Engines.PICOVOICE_CHEETAH:
        if args.picovoice_access_key is None:
            raise ValueError("`picovoice-access-key` is required")
        if args.picovoice_model_path is None and args.language != Languages.EN.value:
            raise ValueError("`picovoice-model-path` is required for non-EN languages")
        engine_params["access_key"] = args.picovoice_access_key
        engine_params["model_path"] = args.picovoice_model_path
        engine_params["library_path"] = args.picovoice_library_path
        engine_params["punctuation"] = False
    elif engine_name in [
        Engines.VOSK_STREAMING_SMALL,
        Engines.VOSK_STREAMING_LARGE,
    ]:
        engine_params["chunk_size_ms"] = args.chunk_size_ms
    elif engine_name in [
        Engines.MOONSHINE_STREAMING_TINY,
        Engines.MOONSHINE_STREAMING_SMALL,
        Engines.MOONSHINE_STREAMING_MEDIUM,
    ]:
        engine_params["chunk_size_ms"] = args.chunk_size_ms
        engine_params["ignore_punctuation"] = True
    elif engine_name in [
        Engines.WHISPER_CPP_STREAMING_TINY,
        Engines.WHISPER_CPP_STREAMING_BASE,
        Engines.WHISPER_CPP_STREAMING_SMALL,
        Engines.WHISPER_CPP_STREAMING_MEDIUM,
        Engines.WHISPER_CPP_STREAMING_LARGE_V3,
        Engines.WHISPER_CPP_STREAMING_LARGE_TURBO,
    ]:
        engine_params["chunk_size_ms"] = args.chunk_size_ms
        engine_params["ignore_punctuation"] = True

    examples = load_alignment_data(dataset_folder)
    random.shuffle(list(examples))
    if args.num_examples is not None:
        examples = examples[:num_examples]

    chunk = math.ceil(len(examples) / num_workers)

    print(f"Processing {len(examples)} examples...")
    futures = []
    with ProcessPoolExecutor(num_workers) as executor:
        for i in range(num_workers):
            future = executor.submit(
                compute_latencies,
                engine_name=engine_name,
                engine_params=engine_params,
                language=language,
                examples=examples[i * chunk : (i + 1) * chunk],
            )
            futures.append(future)

    latencies = []
    for x in futures:
        latencies.extend(x.result())

    avg_latency = int(np.mean(latencies).item() * 1000)
    print(f"Average word emission latency: {avg_latency}ms")

    results_log_path = os.path.join(RESULTS_FOLDER, language.value, f"{str(engine_name)}.log")
    os.makedirs(os.path.dirname(results_log_path), exist_ok=True)
    with open(results_log_path, "w") as f:
        f.write(f"Average word emission latency: {str(avg_latency)}\n")


if __name__ == "__main__":
    main()
