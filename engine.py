import json
import os
import string
import time
import uuid
from enum import Enum

import boto3
import inflect
import pvleopard
import requests
import soundfile
from deepspeech import Model
from google.cloud import speech


class Engines(Enum):
    AMAZON_TRANSCRIBE = "AMAZON_TRANSCRIBE"
    GOOGLE_SPEECH_TO_TEXT = "GOOGLE_SPEECH_TO_TEXT"
    GOOGLE_SPEECH_TO_TEXT_ENHANCED = "GOOGLE_SPEECH_TO_TEXT_ENHANCED"
    MOZILLA_DEEP_SPEECH = 'MOZILLA_DEEP_SPEECH'
    PICOVOICE_CHEETAH = "PICOVOICE_CHEETAH"
    PICOVOICE_LEOPARD = "PICOVOICE_LEOPARD"


class Engine(object):
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def rtf(self) -> float:
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x, **kwargs):
        if x is Engines.AMAZON_TRANSCRIBE:
            return AmazonTranscribeEngine()
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToTextEngine()
        elif x is Engines.MOZILLA_DEEP_SPEECH:
            return MozillaDeepSpeechEngine(**kwargs)
        elif x is Engines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahEngine(**kwargs)
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardEngine(**kwargs)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")

    @classmethod
    def _normalize(cls, text: str) -> str:
        p = inflect.engine()
        text = text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))
        return ' '.join(p.number_to_words(x) if any(c.isdigit() for c in x) else x for x in text.split())


class AmazonTranscribeEngine(Engine):
    def __init__(self):
        self._s3 = boto3.client('s3')
        self._s3_bucket = str(uuid.uuid4())
        self._s3.create_bucket(
            ACL='private',
            Bucket=self._s3_bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

        self._transcribe = boto3.client('transcribe')

    def transcribe(self, path):
        cache_path = path.replace('.flac', '.aws')

        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return f.read()

        job_name = str(uuid.uuid4())
        s3_object = os.path.basename(path)
        self._s3.upload_file(path, self._s3_bucket, s3_object)

        self._transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': 'https://s3-us-west-2.amazonaws.com/%s/%s' % (self._s3_bucket, s3_object)},
            MediaFormat='flac',
            LanguageCode='en-US')

        while True:
            status = self._transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                break
            time.sleep(5)

        content = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])

        res = json.loads(content.content.decode('utf8'))['results']['transcripts'][0]['transcript']
        res = self._normalize(res)

        with open(cache_path, 'w') as f:
            f.write(res)

        return res

    def rtf(self) -> float:
        return -1.

    def delete(self):
        bucket = self._s3.Bucket(self._s3_bucket)
        bucket.objects.all().delete()
        bucket.delete()

    def __str__(self):
        return 'Amazon Transcribe'


class GoogleSpeechToTextEngine(Engine):
    def __init__(self, cache_extension='ggl', model=None):
        self._client = speech.SpeechClient()

        self._config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16000,
            language_code="en-US",
            model=model)

    def transcribe(self, path):
        cache_path = path.replace('.flac', '.ggl')
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return f.read()

        with open(path, 'rb') as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)

        response = self._client.recognize(config=self._config, audio=audio)

        res = ' '.join(result.alternatives[0].transcript for result in response.results)
        res = self._normalize(res)

        with open(cache_path, 'w') as f:
            f.write(res)

        return res

    def rtf(self) -> float:
        return -1.

    def delete(self):
        pass

    def __str__(self):
        return 'Google Speech-to-Text'


class GoogleSpeechToTextEnhancedEngine(GoogleSpeechToTextEngine):
    def __init__(self):
        super().__init__(cache_extension='.ggle', model="video")

    def __str__(self):
        return 'Google Speech-to-Text Enhanced'


class MozillaDeepSpeechEngine(Engine):
    def __init__(self, pbmm_path: str, scorer_path: str):
        self._model = Model(pbmm_path)
        self._model.enableExternalScorer(scorer_path)
        self._audio_sec = 0.
        self._proc_sec = 0.

    def transcribe(self, path):
        audio, sample_rate = soundfile.read(path, dtype='int16')
        assert sample_rate == self._model.sampleRate()
        self._audio_sec += audio.size / sample_rate

        start_sec = time.time()
        res = self._model.stt(audio)
        self._proc_sec += time.time() - start_sec

        return res

    def rtf(self) -> float:
        return self._proc_sec / self._audio_sec

    def delete(self):
        pass

    def __str__(self):
        return 'Mozilla DeepSpeech'


class PicovoiceCheetahEngine(Engine):
    def __init__(self, access_key: str):
        pass

    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def rtf(self) -> float:
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def __str__(self) -> str:
        return 'Picovoice Cheetah'


class PicovoiceLeopardEngine(Engine):
    def __init__(self, access_key: str):
        self._leopard = pvleopard.create(access_key=access_key)
        self._audio_sec = 0.
        self._proc_sec = 0.

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype='int16')
        assert sample_rate == self._leopard.sample_rate
        self._audio_sec += audio.size / sample_rate

        start_sec = time.time()
        res = self._leopard.process(audio)
        self._proc_sec += time.time() - start_sec

        return res

    def rtf(self) -> float:
        return self._proc_sec / self._audio_sec

    def delete(self):
        self._leopard.delete()

    def __str__(self):
        return 'Picovoice Leopard'


__all__ = ['Engines', 'Engine']
