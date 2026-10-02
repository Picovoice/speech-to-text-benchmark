import json
import os
import random
import shutil
import subprocess
import tempfile
from argparse import ArgumentParser
from typing import (
    Sequence,
    Tuple
)

from dataset import (
    Dataset,
    Datasets
)
from languages import Languages


def prepare_mfa_inputs(indices: Sequence[int], dataset: Dataset, corpus_folder: str) -> None:
    for index in indices:
        audio_path, transcript = dataset.get(index)

        shutil.copy2(audio_path, os.path.join(corpus_folder, os.path.basename(audio_path)))

        transcript_file = os.path.join(corpus_folder, f"{os.path.basename(audio_path).split('.')[0]}.txt")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript.strip())


def run_mfa_alignment(corpus_folder: str, work_folder: str, num_workers: int) -> None:
    args = [
        "mfa",
        "align",
        corpus_folder,
        "english_us_arpa",
        "english_us_arpa",
        work_folder,
        "--clean",
        "--num_jobs",
        str(num_workers),
    ]
    print(f"Running MFA alignment: {' '.join(args)}", flush=True)
    subprocess.run(args, check=True)
    print(f"Done MFA alignment: {' '.join(args)}", flush=True)


def parse_textgrid(textgrid_file: str) -> Sequence[Tuple[float, float, str]]:
    alignments = []

    with open(textgrid_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    in_word_tier = False
    in_intervals = False
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if 'name = "words"' in line:
            in_word_tier = True
        elif in_word_tier and "intervals [" in line:
            in_intervals = True
        elif in_word_tier and in_intervals:
            if "xmin = " in line:
                start_time = float(line.split("=")[1].strip())
                i += 1
                if i < len(lines) and "xmax = " in lines[i]:
                    end_time = float(lines[i].split("=")[1].strip())
                    i += 1
                    if i < len(lines) and "text = " in lines[i]:
                        word = lines[i].split("=")[1].strip().strip('"')
                        if word and word not in ["", "sil", "sp"]:
                            alignments.append((start_time, end_time, word))
            elif line.startswith("item [") and "words" not in line:
                break

        i += 1

    return alignments


def generate_alignments(indices: Sequence[int], dataset: Dataset, output_folder: str, num_workers: int):
    with tempfile.TemporaryDirectory() as temp_folder:
        corpus_folder = os.path.join(temp_folder, "corpus")
        work_folder = os.path.join(temp_folder, "work")

        os.makedirs(corpus_folder, exist_ok=True)
        os.makedirs(work_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        prepare_mfa_inputs(indices=indices, dataset=dataset, corpus_folder=corpus_folder)

        run_mfa_alignment(corpus_folder=corpus_folder, work_folder=work_folder, num_workers=num_workers)

        missing_textgrids = []
        for index in indices:
            audio_path, transcript = dataset.get(index)
            basename, format = os.path.splitext(os.path.basename(audio_path))

            textgrid_path = os.path.join(work_folder, f"{basename}.TextGrid")
            if not os.path.isfile(textgrid_path):
                missing_textgrids.append(basename)
                continue

            alignments = parse_textgrid(textgrid_path)

            data = {
                "format": format.lstrip("."),
                "transcript": transcript,
                "alignments": [(start, end) for start, end, _ in alignments],
            }

            with open(os.path.join(output_folder, f"{basename}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            shutil.move(
                os.path.join(corpus_folder, os.path.basename(audio_path)),
                os.path.join(output_folder, os.path.basename(audio_path)),
            )

        if missing_textgrids:
            print(f"MFA failed on {len(missing_textgrids)} of {len(indices)} files")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=[x.value for x in Datasets])
    parser.add_argument("--dataset-folder", required=True)
    parser.add_argument("--language", required=True, choices=[x.value for x in Languages])
    parser.add_argument("--output-folder", required=True)
    parser.add_argument("--num-examples", type=int, default=None)
    parser.add_argument("--num-workers", type=int, default=os.cpu_count())
    args = parser.parse_args()

    dataset = Datasets(args.dataset)
    data_folder = args.dataset_folder
    language = Languages(args.language)
    output_folder = args.output_folder
    num_examples = args.num_examples
    num_workers = args.num_workers

    dataset = Dataset.create(
        dataset,
        folder=data_folder,
        language=language,
        punctuation=False,
        punctuation_set="",
    )

    indices = list(range(dataset.size()))
    random.shuffle(indices)
    if args.num_examples is not None:
        indices = indices[:num_examples]

    generate_alignments(indices=indices, dataset=dataset, output_folder=output_folder, num_workers=num_workers)
