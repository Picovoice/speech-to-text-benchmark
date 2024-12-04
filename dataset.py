import csv
import os
import subprocess
from enum import Enum
from typing import Tuple

import soundfile

from languages import Languages
from normalizer import (
    EnglishNormalizer,
    Normalizer,
)


class Datasets(Enum):
    COMMON_VOICE = "COMMON_VOICE"
    LIBRI_SPEECH_TEST_CLEAN = "LIBRI_SPEECH_TEST_CLEAN"
    LIBRI_SPEECH_TEST_OTHER = "LIBRI_SPEECH_TEST_OTHER"
    TED_LIUM = "TED_LIUM"
    MLS = "MLS"
    VOX_POPULI = "VOX_POPULI"


class Dataset(object):
    def size(self) -> int:
        raise NotImplementedError()

    def get(self, index: int) -> Tuple[str, str]:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x: Datasets, folder: str, language: Languages):
        if x is Datasets.COMMON_VOICE:
            return CommonVoiceDataset(folder, language)
        elif x is Datasets.LIBRI_SPEECH_TEST_CLEAN:
            return LibriSpeechTestCleanDataset(folder, language)
        elif x is Datasets.LIBRI_SPEECH_TEST_OTHER:
            return LibriSpeechTestOtherDataset(folder, language)
        elif x is Datasets.TED_LIUM:
            return TEDLIUMDataset(folder, language)
        elif x is Datasets.MLS:
            return MLSDataset(folder, language)
        elif x is Datasets.VOX_POPULI:
            return VoxPopuliDataset(folder, language)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


class CommonVoiceDataset(Dataset):
    SUPPORTED_LANGUAGES = [
        Languages.DE,
        Languages.EN,
        Languages.ES,
        Languages.FR,
        Languages.IT,
        Languages.PT_BR,
        Languages.PT_PT,
    ]

    def __init__(self, folder: str, language: Languages):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{Datasets.COMMON_VOICE.value} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]}"
            )

        self._language = language
        self._normalizer = Normalizer.create(language)

        self._data = list()
        with open(os.path.join(folder, "test.tsv")) as f:
            reader: csv.DictReader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if int(row["up_votes"]) > 0 and int(row["down_votes"]) == 0:
                    mp3_path = os.path.join(folder, "clips", row["path"])
                    flac_path = mp3_path.replace(".mp3", ".flac")
                    if not os.path.exists(flac_path):
                        args = [
                            "ffmpeg",
                            "-i",
                            mp3_path,
                            "-ac",
                            "1",
                            "-ar",
                            "16000",
                            flac_path,
                        ]
                        subprocess.check_output(args)
                    elif soundfile.read(flac_path)[0].size > 16000 * 60:
                        continue

                    try:
                        self._data.append(
                            (
                                flac_path,
                                self._normalizer.normalize(
                                    row["sentence"],
                                    raise_error_on_invalid_sentence=True,
                                ),
                            )
                        )
                    except RuntimeError:
                        continue

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"CommonVoice {self._language.value}"


class LibriSpeechTestCleanDataset(Dataset):
    SUPPORTED_LANGUAGES = [Languages.EN]

    def __init__(self, folder: str, language: Languages):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{Datasets.LIBRI_SPEECH_TEST_CLEAN.value} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]}"
            )

        self._data = list()
        for speaker_id in os.listdir(folder):
            speaker_folder = os.path.join(folder, speaker_id)
            for chapter_id in os.listdir(speaker_folder):
                chapter_folder = os.path.join(speaker_folder, chapter_id)

                with open(
                    os.path.join(
                        chapter_folder, f"{speaker_id}-{chapter_id}.trans.txt"
                    ),
                    "r",
                ) as f:
                    transcripts = dict(x.split(" ", maxsplit=1) for x in f.readlines())

                for x in os.listdir(chapter_folder):
                    if x.endswith(".flac"):
                        transcript = EnglishNormalizer.normalize(
                            transcripts[x.replace(".flac", "")],
                            raise_error_on_invalid_sentence=True,
                        )
                        self._data.append((os.path.join(chapter_folder, x), transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return "LibriSpeech `test-clean`"


class LibriSpeechTestOtherDataset(LibriSpeechTestCleanDataset):
    def __init__(self, folder: str, language: Languages):
        super().__init__(folder, language)

    def __str__(self) -> str:
        return "LibriSpeech `test-other`"


class TEDLIUMDataset(Dataset):
    SUPPORTED_LANGUAGES = [Languages.EN]

    def __init__(self, folder: str, language: Languages, split_audio: bool = False):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{Datasets.TED_LIUM.value} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]}"
            )

        self._data = list()
        test_folder = os.path.join(folder, "test")
        audio_folder = os.path.join(test_folder, "sph")
        caption_folder = os.path.join(test_folder, "stm")
        for x in os.listdir(caption_folder):
            sph_path = os.path.join(audio_folder, x.replace(".stm", ".sph"))
            full_transcript = ""

            with open(os.path.join(caption_folder, x)) as f:
                for row in csv.reader(f, delimiter=" "):
                    if row[2] == "inter_segment_gap":
                        continue

                    try:
                        transcript = EnglishNormalizer.normalize(
                            " ".join(row[6:]).replace(" '", "'")
                        )
                        full_transcript = (
                            f"{full_transcript} {transcript.strip()}".strip()
                        )
                    except RuntimeError:
                        continue

                    if split_audio:
                        start_sec = float(row[3])
                        end_sec = float(row[4])

                        flac_path = sph_path.replace(
                            ".sph", f"_{start_sec:.3f}_{end_sec:.3f}.flac"
                        )

                        if not os.path.exists(flac_path):
                            args = [
                                "ffmpeg",
                                "-i",
                                sph_path,
                                "-ac",
                                "1",
                                "-ar",
                                "16000",
                                "-loglevel",
                                "error",
                                "-ss",
                                f"{start_sec:.3f}",
                                "-to",
                                f"{end_sec:.3f}",
                                flac_path,
                            ]
                            subprocess.check_output(args)

                        self._data.append((flac_path, transcript))

            if not split_audio:
                flac_path = sph_path.replace(".sph", ".flac")

                if not os.path.exists(flac_path):
                    args = [
                        "ffmpeg",
                        "-i",
                        sph_path,
                        "-ac",
                        "1",
                        "-ar",
                        "16000",
                        "-loglevel",
                        "error",
                        flac_path,
                    ]
                    subprocess.check_output(args)

                self._data.append((flac_path, full_transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return "TED-LIUM"


class MLSDataset(Dataset):
    SUPPORTED_LANGUAGES = [
        Languages.DE,
        Languages.EN,
        Languages.ES,
        Languages.FR,
        Languages.IT,
        Languages.PT_BR,
        Languages.PT_PT,
    ]

    def __init__(self, folder: str, language: Languages):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{Datasets.MLS.value} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]}"
            )

        self._language = language
        self._normalizer = Normalizer.create(language)

        self._data = list()
        with open(os.path.join(folder, "test", "transcripts.txt")) as f:
            for row in f:
                id, transcript = row.split("\t", 1)

                split_id = id.split("_", 2)
                opus_path = os.path.join(
                    folder, "test", "audio", split_id[0], split_id[1], f"{id}.opus"
                )
                flac_path = opus_path.replace(".opus", ".flac")
                if not os.path.exists(flac_path):
                    args = [
                        "ffmpeg",
                        "-i",
                        opus_path,
                        "-ac",
                        "1",
                        "-ar",
                        "16000",
                        flac_path,
                    ]
                    subprocess.check_output(args)

                try:
                    self._data.append(
                        (
                            flac_path,
                            self._normalizer.normalize(
                                transcript,
                                raise_error_on_invalid_sentence=True,
                            ),
                        )
                    )
                except RuntimeError:
                    continue

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"MLS {self._language.value}"


class VoxPopuliDataset(Dataset):
    SUPPORTED_LANGUAGES = [
        Languages.DE,
        Languages.EN,
        Languages.ES,
        Languages.FR,
        Languages.IT,
    ]

    def __init__(self, folder: str, language: Languages):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{Datasets.VOX_POPULI.value} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]}"
            )

        self._language = language
        self._normalizer = Normalizer.create(language)

        self._data = list()
        with open(os.path.join(folder, "asr_test.tsv")) as f:
            reader: csv.DictReader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                year = row["id"][:4]
                ogg_path = os.path.join(folder, year, f"{row['id']}.ogg")
                flac_path = ogg_path.replace(".ogg", ".flac")
                if not os.path.exists(flac_path):
                    args = [
                        "ffmpeg",
                        "-i",
                        ogg_path,
                        "-ac",
                        "1",
                        "-ar",
                        "16000",
                        flac_path,
                    ]
                    subprocess.check_output(args)
                elif soundfile.read(flac_path)[0].size > 16000 * 60:
                    continue

                try:
                    self._data.append(
                        (
                            flac_path,
                            self._normalizer.normalize(
                                row["normalized_text"],
                                raise_error_on_invalid_sentence=True,
                            ),
                        )
                    )
                except RuntimeError:
                    continue

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"Vox Populi {self._language.value}"


__all__ = [
    "Dataset",
    "Datasets",
]
