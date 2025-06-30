import csv
import os
import subprocess
from enum import Enum
from typing import (
    Sequence,
    Tuple
)

import soundfile

from languages import Languages
from normalizer import Normalizer


class Datasets(Enum):
    COMMON_VOICE = "COMMON_VOICE"
    FLEURS = "FLEURS"
    LIBRI_SPEECH_TEST_CLEAN = "LIBRI_SPEECH_TEST_CLEAN"
    LIBRI_SPEECH_TEST_OTHER = "LIBRI_SPEECH_TEST_OTHER"
    MLS = "MLS"
    TED_LIUM = "TED_LIUM"
    VOX_POPULI = "VOX_POPULI"


class Dataset(object):
    SUPPORTED_LANGUAGES: Sequence[Languages] = []
    SUPPORTS_PUNCTUATION: bool = False

    def __init__(self, language: Languages, punctuation: bool, dataset_name: str):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"{dataset_name} dataset only supports {[lang.value for lang in self.SUPPORTED_LANGUAGES]} languages"
            )
        if punctuation and not self.SUPPORTS_PUNCTUATION:
            raise ValueError(f"{dataset_name} dataset does not support punctuation")
        self._language = language

    def size(self) -> int:
        raise NotImplementedError()

    def get(self, index: int) -> Tuple[str, str]:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(
        cls, x: Datasets, folder: str, language: Languages, punctuation: bool, punctuation_set: str
    ):
        normalizer = Normalizer.create(
            language=language,
            keep_punctuation=punctuation,
            punctuation_set=punctuation_set,
        )

        if x is Datasets.COMMON_VOICE:
            return CommonVoiceDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.LIBRI_SPEECH_TEST_CLEAN:
            return LibriSpeechTestCleanDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.LIBRI_SPEECH_TEST_OTHER:
            return LibriSpeechTestOtherDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.TED_LIUM:
            return TEDLIUMDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.MLS:
            return MLSDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.VOX_POPULI:
            return VoxPopuliDataset(folder, language, punctuation, normalizer)
        elif x is Datasets.FLEURS:
            return FleursDataset(folder, language, punctuation, normalizer)
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
    SUPPORTS_PUNCTUATION = True

    def __init__(self, folder: str, language: Languages, punctuation: bool, normalizer: Normalizer):
        super().__init__(language, punctuation, Datasets.COMMON_VOICE.value)

        self._language = language

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
                        transcript = normalizer.normalize(row["sentence"], raise_error_on_invalid_sentence=True)
                    except RuntimeError:
                        continue

                    if punctuation and transcript[-1] not in [".", "?"]:
                        continue

                    self._data.append((flac_path, transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"CommonVoice {self._language.value}"


class LibriSpeechTestCleanDataset(Dataset):
    SUPPORTED_LANGUAGES = [Languages.EN]
    SUPPORTS_PUNCTUATION = False

    def __init__(
        self,
        folder: str,
        language: Languages,
        punctuation: bool,
        normalizer: Normalizer,
        dataset_name: str = Datasets.LIBRI_SPEECH_TEST_CLEAN.value,
    ):
        super().__init__(language, punctuation, dataset_name)

        self._data = list()
        for speaker_id in os.listdir(folder):
            speaker_folder = os.path.join(folder, speaker_id)
            for chapter_id in os.listdir(speaker_folder):
                chapter_folder = os.path.join(speaker_folder, chapter_id)

                with open(
                    os.path.join(chapter_folder, f"{speaker_id}-{chapter_id}.trans.txt"),
                    "r",
                ) as f:
                    transcripts = dict(x.split(" ", maxsplit=1) for x in f.readlines())

                for x in os.listdir(chapter_folder):
                    if x.endswith(".flac"):
                        transcript = normalizer.normalize(
                            transcripts[x.replace(".flac", "")], raise_error_on_invalid_sentence=True
                        )
                        self._data.append((os.path.join(chapter_folder, x), transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return "LibriSpeech `test-clean`"


class LibriSpeechTestOtherDataset(LibriSpeechTestCleanDataset):
    def __init__(
        self,
        folder: str,
        language: Languages,
        punctuation: bool,
        normalizer: Normalizer,
    ):
        super().__init__(folder, language, punctuation, normalizer, Datasets.LIBRI_SPEECH_TEST_OTHER.value)

    def __str__(self) -> str:
        return "LibriSpeech `test-other`"


class TEDLIUMDataset(Dataset):
    SUPPORTED_LANGUAGES = [Languages.EN]
    SUPPORTS_PUNCTUATION = False

    def __init__(
        self, folder: str, language: Languages, punctuation: bool, normalizer: Normalizer, split_audio: bool = False
    ):
        super().__init__(language, punctuation, Datasets.TED_LIUM.value)

        self._data = list()
        test_folder = os.path.join(folder, "test")
        audio_folder = os.path.join(test_folder, "sph")
        caption_folder = os.path.join(test_folder, "stm")
        for x in os.listdir(caption_folder):
            sph_path = os.path.join(audio_folder, x.replace(".stm", ".sph"))
            full_transcript = ""
            last_row = None

            with open(os.path.join(caption_folder, x)) as f:
                for row in csv.reader(f, delimiter=" "):
                    last_row = row

                    if row[2] == "inter_segment_gap":
                        continue

                    try:
                        transcript = normalizer.normalize(" ".join(row[6:]).replace(" '", "'"))
                        full_transcript = f"{full_transcript} {transcript.strip()}".strip()
                    except RuntimeError:
                        continue

                    if split_audio:
                        start_sec = float(row[3])
                        end_sec = float(row[4])

                        flac_path = sph_path.replace(".sph", f"_{start_sec:.3f}_{end_sec:.3f}.flac")

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
                    if last_row is not None and last_row[2] == "inter_segment_gap":
                        end_sec = float(last_row[3])

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
                            "0",
                            "-to",
                            f"{end_sec:.3f}",
                            flac_path,
                        ]
                    else:
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
    SUPPORTS_PUNCTUATION = False

    def __init__(self, folder: str, language: Languages, punctuation: bool, normalizer: Normalizer):
        super().__init__(language, punctuation, Datasets.MLS.value)

        self._language = language

        self._data = list()
        with open(os.path.join(folder, "test", "transcripts.txt")) as f:
            for row in f:
                id, transcript = row.split("\t", 1)

                split_id = id.split("_", 2)
                opus_path = os.path.join(folder, "test", "audio", split_id[0], split_id[1], f"{id}.opus")
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
                            normalizer.normalize(transcript, raise_error_on_invalid_sentence=True),
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
    SUPPORTS_PUNCTUATION = True

    def __init__(self, folder: str, language: Languages, punctuation: bool, normalizer: Normalizer):
        super().__init__(language, punctuation, Datasets.VOX_POPULI.value)

        self._language = language

        if punctuation:
            self._data = self._load_punctuation_data(folder, normalizer)
        else:
            self._data = self._load_data(folder, normalizer)

    @staticmethod
    def _load_data(folder: str, normalizer: Normalizer):
        data = list()
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
                    data.append(
                        (
                            flac_path,
                            normalizer.normalize(
                                row["normalized_text"],
                                raise_error_on_invalid_sentence=True,
                            ),
                        )
                    )
                except RuntimeError:
                    continue

        return data

    @staticmethod
    def _load_punctuation_data(folder: str, normalizer: Normalizer):
        data = list()
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

                transcript = row["raw_text"]

                if len(transcript) == 0:
                    continue

                if any(c.isdigit() for c in transcript):
                    continue

                try:
                    data.append(
                        (
                            flac_path,
                            normalizer.normalize(transcript, raise_error_on_invalid_sentence=True),
                        )
                    )
                except RuntimeError:
                    continue

        return data

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"Vox Populi {self._language.value}"


class FleursDataset(Dataset):
    SUPPORTED_LANGUAGES = [
        Languages.DE,
        Languages.EN,
        Languages.ES,
        Languages.FR,
        Languages.IT,
        Languages.PT_BR,
        Languages.PT_PT,
    ]
    SUPPORTS_PUNCTUATION = True

    def __init__(self, folder: str, language: Languages, punctuation: bool, normalizer: Normalizer):
        super().__init__(language, punctuation, Datasets.FLEURS.value)

        self._language = language

        self._data = list()
        with open(os.path.join(folder, "test.tsv")) as f:
            fieldnames = ["id", "filename", "raw_text", "normalized_text", "phonemes", "duration", "gender"]
            reader = csv.DictReader(f, delimiter="\t", fieldnames=fieldnames)
            for row in reader:
                wav_path = os.path.join(folder, "audio", "test", row["filename"])
                flac_path = wav_path.replace(".wav", ".flac")
                if not os.path.exists(flac_path):
                    args = [
                        "ffmpeg",
                        "-i",
                        wav_path,
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
                            normalizer.normalize(
                                row["raw_text"] if punctuation else row["normalized_text"],
                                raise_error_on_invalid_sentence=True,
                            ),
                        )
                    )
                except RuntimeError as e:
                    continue

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return f"Fleurs {self._language.value}"


__all__ = [
    "Dataset",
    "Datasets",
]
