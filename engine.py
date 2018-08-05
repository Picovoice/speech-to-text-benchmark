import os
import subprocess
from enum import Enum

import numpy as np
import soundfile
from deepspeech.model import Model
from pocketsphinx import get_model_path
from pocketsphinx.pocketsphinx import Decoder


class ASREngines(Enum):
    """Speech recognition engines"""

    MOZILLA_DEEP_SPEECH = 'DeepSpeech'
    PICOVOICE_CHEETAH = "Cheetah"
    POCKET_SPHINX = 'PocketSphinx'


class ASREngine(object):
    """Base class for a speech recognition engine."""

    def transcribe(self, path):
        """
        Given path to an audio file returns transcribed text.

        :param path: Absolute path to audio file containing speech to be transcribed.
        :return: Transcribed speech.
        """

        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, engine_type, **kwargs):
        """
        Factory method.

        :param engine_type: Type of engine.
        :param kwargs: Keyword arguments.
        :return: Speech recognition object.
        """

        if engine_type is ASREngines.MOZILLA_DEEP_SPEECH:
            return MozillaDeepSpeechASREngine(**kwargs)
        elif engine_type is ASREngines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahASREngine()
        elif engine_type is ASREngines.POCKET_SPHINX:
            return PocketSphinxASREngine()
        else:
            raise ValueError("cannot create %s of type '%s'" % (cls.__name__, engine_type))


class PocketSphinxASREngine(ASREngine):
    """https://pypi.org/project/pocketsphinx/"""

    def __init__(self):
        # https://github.com/cmusphinx/pocketsphinx-python/blob/master/example.py
        config = Decoder.default_config()
        config.set_string('-logfn', '/dev/null')
        config.set_string('-hmm', os.path.join(get_model_path(), 'en-us'))
        config.set_string('-lm', os.path.join(get_model_path(), 'en-us.lm.bin'))
        config.set_string('-dict', os.path.join(get_model_path(), 'cmudict-en-us.dict'))

        self._decoder = Decoder(config)

    def transcribe(self, path):
        pcm, sample_rate = soundfile.read(path)
        assert sample_rate == 16000
        pcm = (np.iinfo(np.int16).max * pcm).astype(np.int16).tobytes()

        self._decoder.start_utt()
        self._decoder.process_raw(pcm, no_search=False, full_utt=True)
        self._decoder.end_utt()

        words = []
        for seg in self._decoder.seg():
            word = seg.word

            # Remove special tokens.
            if word == '<sil>' or word == '<s>' or word == '</s>':
                continue

            word = ''.join([x for x in word if x.isalpha()])

            words.append(word)

        return ' '.join(words)

    def __str__(self):
        return 'PocketSphinx'


class MozillaDeepSpeechASREngine(ASREngine):
    """https://github.com/mozilla/DeepSpeech"""

    def __init__(self, model_path, alphabet_path, language_model_path=None, trie_path=None):
        """
        Constructor.

        :param model_path: Absolute path to (acoustic) model file.
        :param alphabet_path: Absolute path to file containing alphabet.
        :param language_model_path: Absolute path to language model file. This parameter is optional. Set to
        enable decoding with language model.
        :param trie_path: Absolute path to trie. This parameter is optional. Set to enable decoding with language model.
        """

        # https://github.com/mozilla/DeepSpeech/blob/master/native_client/python/client.py
        self._model = Model(
            aModelPath=model_path,
            aNCep=26,
            aNContext=9,
            aAlphabetConfigPath=alphabet_path,
            aBeamWidth=500)

        if language_model_path is not None and trie_path is not None:
            self._model.enableDecoderWithLM(
                aAlphabetConfigPath=alphabet_path,
                aLMPath=language_model_path,
                aTriePath=trie_path,
                aLMWeight=1.75,
                aWordCountWeight=1.0,
                aValidWordCountWeight=1.0)
            self._with_language_model = True
        else:
            self._with_language_model = False

    def transcribe(self, path):
        pcm, sample_rate = soundfile.read(path)
        pcm = (np.iinfo(np.int16).max * pcm).astype(np.int16)

        return self._model.stt(pcm, aSampleRate=sample_rate)

    def __str__(self):
        if self._with_language_model:
            return 'Mozilla DeepSpeech (with language model)'
        else:
            return 'Mozilla DeepSpeech'


class PicovoiceCheetahASREngine(ASREngine):
    """http://picovoice.ai/"""

    def transcribe(self, path):
        cheetah_dir = os.path.join(os.path.dirname(__file__), 'resources/cheetah')
        cheetah_app_path = os.path.join(cheetah_dir, 'pv_cheetah_app')
        cheetah_param_path = os.path.join(cheetah_dir, 'cheetah_params.pv')
        cheetah_license_path = os.path.join(cheetah_dir, 'cheetah_linux_eval.lic')

        args = [cheetah_app_path, path, cheetah_param_path, cheetah_license_path]
        res = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')

        if 'ERROR' in res:
            raise Exception("transcription failed with message:\n'%s'" % res)

        return res.strip('\n ')

    def __str__(self):
        return 'Picovoice Cheetah'
