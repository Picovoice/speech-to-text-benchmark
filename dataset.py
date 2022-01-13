import csv
import os
import string
import subprocess
from enum import Enum
from typing import Tuple

import inflect
from pytube import YouTube


class Datasets(Enum):
    ASSEMBLY_AI = 'ASSEMBLY_AI'
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
        if x == Datasets.ASSEMBLY_AI:
            return AssemblyAIDataset(folder)
        elif x == Datasets.COMMON_VOICE:
            return CommonVoiceDataset(folder)
        elif x == Datasets.LIBRI_SPEECH:
            return LibriSpeechDataset(folder)
        elif x == Datasets.TEDLIUM:
            return TEDLIUMDataset(folder)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")

    @staticmethod
    def _normalize(text: str) -> str:
        p = inflect.engine()
        text = text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))
        return ' '.join(p.number_to_words(x) if any(c.isdigit() for c in x) else x for x in text.split())


class AssemblyAIDataset(Dataset):
    def size(self) -> int:
        pass

    def get(self, index: int) -> Tuple[str, str]:
        pass

    def __str__(self) -> str:
        pass

    _URLS = [
        'https://www.youtube.com/watch?v=1kNgGsp7f8c',
        'https://www.youtube.com/watch?v=LpSyfx3G7p4',
        'https://www.youtube.com/watch?v=HwUGGry85AU',
        'https://www.youtube.com/watch?v=4jnwNs_kmCA',
        'https://www.youtube.com/watch?v=YYoKapX4Des',
        'https://www.youtube.com/watch?v=ColSssdJnKE',
        'https://www.youtube.com/watch?v=307gHJHd8Ko',
        'https://www.youtube.com/watch?v=PeeL4TV4CvI',
        'https://www.youtube.com/watch?v=_q_bWATVJTg',
        'https://www.youtube.com/watch?v=pDeZFrgNVwI',
        'https://www.youtube.com/watch?v=wnNeH1aVHCM',
        'https://www.youtube.com/watch?v=p_MxhPKPAqA',
        'https://www.youtube.com/watch?v=NvCMWEWckw8',
        'https://www.youtube.com/watch?v=NGPSCR69G-I',
        'https://www.youtube.com/watch?v=y2A0qbd_x9A',
        'https://www.youtube.com/watch?v=AwklziE5HKo',
        'https://www.youtube.com/watch?v=AkcwNwPy7RI',
    ]

    def __init__(self, folder):
        for url in self._URLS:
            webm_path = os.path.join(folder, f'{url.split("watch?v=")[1]}.webm')
            if not os.path.exists(webm_path):
                youtube = YouTube(url)
                audio_stream = youtube.streams.filter(only_audio=True, audio_codec='opus').order_by('bitrate').last()
                audio_stream.download(output_path=folder, filename=os.path.basename(webm_path), skip_existing=True)

            flac_path = webm_path.replace('.webm', '.flac')
            if not os.path.exists(flac_path):
                subprocess.check_output(
                    f'ffmpeg -y -i {webm_path} -f wav -fflags bitexact -ac 1 -ar 16000 -acodec pcm_s16le {flac_path}',
                    stderr=subprocess.STDOUT,
                    shell=True)

            caption_path = webm_path.replace('.webm', '.cap')
            if not os.path.exists(caption_path):
                captions = YouTube(url).captions

                if 'en' in captions:
                    key = 'en'
                elif 'a.en' in captions:
                    key = 'a.en'
                else:
                    raise RuntimeError(f"`{url}` doesn't have any EN captions. It has `{' '.join(captions.keys())}`")

                with open(caption_path, 'w') as f:
                    f.write(captions[key].xml_captions)


class CommonVoiceDataset(Dataset):
    def __init__(self, folder: str):
        self._data = list()
        with open(os.path.join(folder, 'test.tsv')) as f:
            for row in csv.DictReader(f, delimiter='\t'):
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

                    self._data.append((flac_path, self._normalize(row['sentence'])))

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

        test_folder = os.path.join(folder, 'test')
        audio_folder = os.path.join(test_folder, 'sph')
        caption_folder = os.path.join(test_folder, 'stm')
        for x in os.listdir(caption_folder):
            with open(os.path.join(caption_folder, x)) as f:
                for row in csv.reader(f, delimiter=" "):
                    if row[2] == "inter_segment_gap":
                        continue
                    start_sec = float(row[3])
                    end_sec = float(row[4])

                    transcript = self._normalize(" ".join(row[6:]).replace(" '", "'"))

                    sph_path = os.path.join(audio_folder, x.replace('.stm', '.sph'))
                    flac_path = sph_path.replace('.sph', f'_{start_sec:.3f}_{end_sec:.3f}.flac')

                    if not os.path.exists(flac_path):
                        args = [
                            'ffmpeg',
                            '-i',
                            sph_path,
                            '-ac', '1',
                            '-ar', '16000',
                            '-ss', f'{start_sec:.3f}',
                            '-to', f'{end_sec:.3f}',
                            flac_path,
                        ]
                        subprocess.check_output(args)

                    self._data.append((flac_path, transcript))

    def size(self) -> int:
        return len(self._data)

    def get(self, index: int) -> Tuple[str, str]:
        return self._data[index]

    def __str__(self) -> str:
        return 'TEDLIUM'


__all__ = ['Datasets', 'Dataset']


def main():
    o = AssemblyAIDataset(folder=os.path.expanduser('~/work/data/speech/AssemblyAI'))


if __name__ == '__main__':
    main()
