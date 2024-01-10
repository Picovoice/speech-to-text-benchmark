import csv
import os
import subprocess
from enum import Enum
from typing import Tuple

import soundfile

from normalizer import Normalizer


class Datasets(Enum):
    COMMON_VOICE = 'COMMON_VOICE'
    LIBRI_SPEECH_TEST_CLEAN = 'LIBRI_SPEECH_TEST_CLEAN'
    LIBRI_SPEECH_TEST_OTHER = 'LIBRI_SPEECH_TEST_OTHER'
    TED_LIUM = 'TED_LIUM'


class Dataset(object):
    def size(self) -> int:
        raise NotImplementedError()

    def get(self, index: int) -> Tuple[str, str]:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x: Datasets, folder: str):
        if x is Datasets.COMMON_VOICE:
            return CommonVoiceDataset(folder)
        elif x is Datasets.LIBRI_SPEECH_TEST_CLEAN:
            return LibriSpeechTestCleanDataset(folder)
        elif x is Datasets.LIBRI_SPEECH_TEST_OTHER:
            return LibriSpeechTestOtherDataset(folder)
        elif x is Datasets.TED_LIUM:
            return TEDLIUMDataset(folder)
        elif x is Datasets.PODCAST:
            return PodcastDataset()
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


class CommonVoiceDataset(Dataset):
    def __init__(self, folder: str):
        normalizer = Normalizer()
        self._data = list()
        with open(os.path.join(folder, 'test.tsv')) as f:
            reader: csv.DictReader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if int(row['up_votes']) > 0 and int(row['down_votes']) == 0:
                    mp3_path = os.path.join(folder, 'clips', row['path'])
                    flac_path = mp3_path.replace('.mp3', '.flac')
                    if not os.path.exists(flac_path):
                        args = [
                            'ffmpeg',
                            '-i',
                            mp3_path,
                            '-ac', '1',
                            '-ar', '16000',
                            flac_path,
                        ]
                        subprocess.check_output(args)
                    elif soundfile.read(flac_path)[0].size > 16000 * 60:
                        continue

                    try:
                        self._data.append((flac_path, normalizer.normalize(row['sentence'])))
                    except RuntimeError:
                        continue

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'CommonVoice'


class LibriSpeechTestCleanDataset(Dataset):
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
        return 'LibriSpeech `test-clean`'


class LibriSpeechTestOtherDataset(LibriSpeechTestCleanDataset):
    def __init__(self, folder: str):
        super().__init__(folder)

    def __str__(self) -> str:
        return 'LibriSpeech `test-other`'


class TEDLIUMDataset(Dataset):
    def __init__(self, folder: str, split_audio: bool = False):
        normalizer = Normalizer()
        self._data = list()
        test_folder = os.path.join(folder, 'test')
        audio_folder = os.path.join(test_folder, 'sph')
        caption_folder = os.path.join(test_folder, 'stm')
        for x in os.listdir(caption_folder):
            sph_path = os.path.join(audio_folder, x.replace('.stm', '.sph'))
            full_transcript = ""

            with open(os.path.join(caption_folder, x)) as f:
                for row in csv.reader(f, delimiter=" "):
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

                        flac_path = sph_path.replace('.sph', f'_{start_sec:.3f}_{end_sec:.3f}.flac')

                        if not os.path.exists(flac_path):
                            args = [
                                'ffmpeg',
                                '-i',
                                sph_path,
                                '-ac', '1',
                                '-ar', '16000',
                                '-loglevel', 'error',
                                '-ss', f'{start_sec:.3f}',
                                '-to', f'{end_sec:.3f}',
                                flac_path,
                            ]
                            subprocess.check_output(args)

                        self._data.append((flac_path, transcript))

            if not split_audio:
                flac_path = sph_path.replace('.sph', '.flac')

                if not os.path.exists(flac_path):
                    args = [
                        'ffmpeg',
                        '-i',
                        sph_path,
                        '-ac', '1',
                        '-ar', '16000',
                        '-loglevel', 'error',
                        flac_path,
                    ]
                    subprocess.check_output(args)

                self._data.append((flac_path, full_transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'TED-LIUM'


__all__ = ['Datasets', 'Dataset']
