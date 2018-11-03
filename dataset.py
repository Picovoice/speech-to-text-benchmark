import csv
import os

import soundfile
import sox


class Dataset(object):
    """Base class for speech corpus."""

    def size(self):
        """Number of examples (audio files) in dataset."""

        raise NotImplementedError()

    def size_hours(self):
        """Total size of dataset in terms of hours of speech data."""

        return sum([soundfile.read(self.get(i)[0])[0].size / (16000 * 3600) for i in range(self.size())])

    def get(self, index):
        """
        Returns path to audio file and its corresponding transcription.

        :param index: data index
        :return: tuple of audio file path and reference transcription.
        """
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, dataset_type, root):
        """
        Factory method.

        :param dataset_type: Type of dataset.
        :param root: Absolute path to root of dataset.
        :return: Dataset object.
        """

        if dataset_type == 'commonvoice':
            return CommonVoiceDataset(root)
        if dataset_type == 'librispeech':
            return LibriSpeechDataset(root)
        else:
            raise ValueError("cannot create %s of type '%s'" % (cls.__name__, dataset_type))


class CommonVoiceDataset(Dataset):
    """https://voice.mozilla.org/en"""

    def __init__(self, root):
        """
        Constructor. It converts MP3 files into WAV files as Cheetah can only consume WAV.

        :param root: root of dataset.
        """

        self._data = []

        metadata_path = os.path.join(root, 'cv-valid-test.csv')
        with open(metadata_path) as f:
            reader = csv.DictReader(f)

            for row in reader:
                text = row['text'].lower()
                up_votes = int(row['up_votes'])
                down_votes = int(row['down_votes'])

                # NOTE: perform some basics checks to ensure the validity of data
                if up_votes < 2 or down_votes > 0 or len(text) == 0:
                    continue

                mp3_path = os.path.join(root, row['filename'])
                wav_path = mp3_path.replace('.mp3', '.wav')
                if not os.path.exists(wav_path):
                    transformer = sox.Transformer()
                    transformer.convert(samplerate=16000, bitdepth=16, n_channels=1)
                    transformer.build(mp3_path, wav_path)

                self._data.append((wav_path, text))

    def size(self):
        return len(self._data)

    def get(self, index):
        return self._data[index]

    def __str__(self):
        return 'Common Voice Dataset'


class LibriSpeechDataset(Dataset):
    def __init__(self, root):
        self._data = list()

        for speaker_id in os.listdir(root):
            speaker_dir = os.path.join(root, speaker_id)

            for chapter_id in os.listdir(speaker_dir):
                chapter_dir = os.path.join(speaker_dir, chapter_id)

                transcript_path = os.path.join(chapter_dir, '%s-%s.trans.txt' % (speaker_id, chapter_id))
                with open(transcript_path, 'r') as f:
                    transcripts = dict([tuple(x.split(' ', maxsplit=1)) for x in f.readlines()])

                for flac_file in os.listdir(chapter_dir):
                    if flac_file.endswith('.flac'):
                        wav_file = flac_file.replace('.flac', '.wav')
                        wav_path = os.path.join(chapter_dir, wav_file)
                        if not os.path.exists(wav_path):
                            flac_path = os.path.join(chapter_dir, flac_file)
                            pcm, sample_rate = soundfile.read(flac_path)
                            soundfile.write(wav_path, pcm, sample_rate)

                        self._data.append((wav_path, transcripts[wav_file.replace('.wav', '')]))

    def size(self):
        return len(self._data)

    def get(self, index):
        return self._data[index]

    def __str__(self):
        return 'LibriSpeech Dataset'
