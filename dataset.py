import csv
import os
import string
import subprocess
from enum import Enum
from typing import Tuple

import inflect


class Datasets(Enum):
    COMMON_VOICE = 'COMMON_VOICE'
    LIBRI_SPEECH = 'LIBRI_SPEECH'
    TEDLIUM = 'TEDLIUM'


class Dataset(object):
    def size(self) -> int:
        raise NotImplementedError()

    def get(self, index: int) -> Tuple[str, str]:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x: Datasets, folder: str):
        if x == Datasets.LIBRI_SPEECH:
            return LibriSpeechDataset(folder)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")

    @staticmethod
    def _normalize(text: str) -> str:
        p = inflect.engine()
        text = text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))
        return ' '.join(p.number_to_words(x) if any(c.isdigit() for c in x) else x for x in text.split())


class CommonVoiceDataset(Dataset):
    def __init__(self, folder: str):
        self._data = list()
        with open(os.path.join(folder, 'test.tsv')) as f:
            for row in csv.DictReader(f, delimiter='\t'):
                if int(row['up_votes']) > 0 and int(row['down_votes']) == 0:
                    self._data.append((os.path.join(folder, 'clips', row['path']), self._normalize(row['sentence'])))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'CommonVoice'


class LibriSpeechDataset(Dataset):
    def __init__(self, folder: str):
        self._data = list()

        for speaker_id in os.listdir(folder):
            speaker_folder = os.path.join(folder, speaker_id)
            for chapter_id in os.listdir(speaker_folder):
                chapter_folder = os.path.join(speaker_folder, chapter_id)

                with open(os.path.join(chapter_folder, f'{speaker_id}-{chapter_id}.trans.txt'), 'r') as f:
                    transcripts = dict(x.split(' ', maxsplit=1) for x in f.readlines())

                for x in os.listdir(chapter_folder):
                    if x.endswith('.flac'):
                        self._data.append((os.path.join(chapter_folder, x), transcripts[x.replace('.flac', '')]))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'LibriSpeech'


class TEDLIUMDataset(Dataset):
    def __init__(self, folder: str):
        self._data = list()

        data_dir = os.path.join(folder, 'test')
        audio_path = os.path.join(data_dir, 'sph')
        ref_path = os.path.join(data_dir, 'stm')
        for stm_file in os.listdir(ref_path):
            stm_path = os.path.join(ref_path, stm_file)
            with open(stm_path) as f:
                rd = csv.reader(f, delimiter=" ")

                count = 0
                for row in rd:
                    if row[2] == "inter_segment_gap":
                        continue
                    start = row[3]
                    end = row[4]
                    transcript = " ".join(row[6:])
                    transcript = transcript.replace(" '", "'")
                    transcript = self._normalize(transcript)

                    sph_file = stm_file.replace('.stm', '.sph')
                    wav_file = stm_file.replace('.stm', '_{:04d}.wav'.format(count))
                    wav_path = os.path.join(audio_path, wav_file)

                    if not os.path.exists(wav_path):
                        sph_path = os.path.join(audio_path, sph_file)
                        subprocess.run(['sph2pipe', '-f', 'wav', '-p', '-c', '1', sph_path, wav_path,
                                        '-t', "{}:{}".format(start, end)])

                    self._data.append((wav_path, transcript))
                    count += 1

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'TEDLIUM'


__all__ = ['Datasets', 'Dataset']
