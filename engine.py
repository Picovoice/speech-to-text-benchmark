import json
import os
import string
import time
import uuid
from enum import Enum

import boto3
import numpy as np
import pvleopard
import requests
import soundfile
from deepspeech import Model
from google.cloud import speech


class Engines(Enum):
    AMAZON_TRANSCRIBE = "AMAZON_TRANSCRIBE"
    GOOGLE_SPEECH_TO_TEXT = "GOOGLE_SPEECH_TO_TEXT"
    MOZILLA_DEEP_SPEECH = 'MOZILLA_DEEP_SPEECH'
    PICOVOICE_CHEETAH = "PICOVOICE_CHEETAH"
    PICOVOICE_LEOPARD = "PICOVOICE_LEOPARD"


class Engine(object):
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def proc_sec(self) -> float:
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
            return MozillaDeepSpeechEngine()
        elif x is Engines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahEngine(**kwargs)
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardEngine(**kwargs)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


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
        cache_path = path.replace('.wav', '.aws')

        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return f.read()

        job_name = str(uuid.uuid4())
        s3_object = os.path.basename(path)
        self._s3.upload_file(path, self._s3_bucket, s3_object)

        self._transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': 'https://s3-us-west-2.amazonaws.com/%s/%s' % (self._s3_bucket, s3_object)},
            MediaFormat='wav',
            LanguageCode='en-US')

        while True:
            status = self._transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] is 'COMPLETED':
                break
            time.sleep(5)

        content = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])

        res = json.loads(content.content.decode('utf8'))['results']['transcripts'][0]['transcript']
        res = res.translate(str.maketrans('', '', string.punctuation))

        with open(cache_path, 'w') as f:
            f.write(res)

        return res

    def proc_sec(self) -> float:
        raise NotImplementedError()

    def __str__(self):
        return 'Amazon Transcribe'


class GoogleSpeechToTextEngine(Engine):
    def __init__(self):
        self._client = speech.SpeechClient()

    def transcribe(self, path):
        pass
        # cache_path = path.replace('.wav', '.ggl')
        # if os.path.exists(cache_path):
        #     with open(cache_path) as f:
        #         return f.read()
        #
        # with open(path, 'rb') as f:
        #     content = f.read()
        #
        # audio = types.RecognitionAudio(content=content)
        # config = types.RecognitionConfig(
        #     encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        #     sample_rate_hertz=16000,
        #     language_code='en-US')
        #
        # response = self._client.recognize(config, audio)
        #
        # res = ' '.join(result.alternatives[0].transcript for result in response.results)
        # res = res.translate(str.maketrans('', '', string.punctuation))
        #
        # with open(cache_path, 'w') as f:
        #     f.write(res)
        #
        # return res

    def proc_sec(self) -> float:
        raise NotImplementedError()

    def __str__(self):
        return 'Google Speech-to-Text'


class MozillaDeepSpeechEngine(Engine):
    def __init__(self, pbmm_path: str, scorer_path: str):
        self._model = Model(pbmm_path)
        self._model.enableExternalScorer(scorer_path)
        self._proc_sec = 0.

    def transcribe(self, path):
        start_sec = time.time()
        res = self._model.stt(soundfile.read(path, dtype='int16'))
        self._proc_sec += time.time() - start_sec

        return res

    def proc_sec(self) -> float:
        return self._proc_sec

    def __str__(self):
        return 'Mozilla DeepSpeech'


class PicovoiceCheetahEngine(Engine):
    def __init__(self, access_key: str):
        pass

    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def proc_sec(self) -> float:
        raise NotImplementedError()

    def __str__(self) -> str:
        return 'Picovoice Cheetah'


class PicovoiceLeopardEngine(Engine):
    def __init__(self, access_key: str):
        self._proc_sec = 0.
        self._leopard = pvleopard.create(access_key=access_key)

    def transcribe(self, path: str) -> str:
        start_sec = time.time()
        res = self._leopard.process_file(path)
        self._proc_sec += time.time() - start_sec

        return res

    def proc_sec(self) -> float:
        return self._proc_sec

    def __str__(self):
        return 'Picovoice Leopard'


__all__ = ['Engines', 'Engine']
