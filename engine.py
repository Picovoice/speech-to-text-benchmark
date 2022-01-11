import json
import os
import string
import subprocess
import time
import uuid
from enum import Enum

import boto3
import numpy as np
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
    def transcribe(self, path):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, x):
        if x is Engines.AMAZON_TRANSCRIBE:
            return AmazonTranscribe()
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToText()
        elif x is Engines.MOZILLA_DEEP_SPEECH:
            return MozillaDeepSpeechASREngine()
        elif x is Engines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahASREngine()
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardASREngine()
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


class AmazonTranscribe(Engine):
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

    def __str__(self):
        return 'Amazon Transcribe'


class GoogleSpeechToText(Engine):
    def __init__(self):
        self._client = speech.SpeechClient()

    def transcribe(self, path):
        cache_path = path.replace('.wav', '.ggl')
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return f.read()

        with open(path, 'rb') as f:
            content = f.read()

        audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US')

        response = self._client.recognize(config, audio)

        res = ' '.join(result.alternatives[0].transcript for result in response.results)
        res = res.translate(str.maketrans('', '', string.punctuation))

        with open(cache_path, 'w') as f:
            f.write(res)

        return res

    def __str__(self):
        return 'Google Speech-to-Text'


class MozillaDeepSpeechASREngine(Engine):
    def __init__(self):
        deepspeech_dir = os.path.join(os.path.dirname(__file__), 'res/deepspeech')
        model_path = os.path.join(deepspeech_dir, 'output_graph.pbmm')
        alphabet_path = os.path.join(deepspeech_dir, 'alphabet.txt')
        language_model_path = os.path.join(deepspeech_dir, 'lm.binary')
        trie_path = os.path.join(deepspeech_dir, 'trie')

        # https://github.com/mozilla/DeepSpeech/blob/master/native_client/python/client.py
        self._model = Model(model_path, 500)
        self._model.enableDecoderWithLM(language_model_path, trie_path, 0.75, 1.85)

    def transcribe(self, path):
        pcm, sample_rate = soundfile.read(path)
        pcm = (np.iinfo(np.int16).max * pcm).astype(np.int16)
        res = self._model.stt(pcm)

        return res

    def __str__(self):
        return 'Mozilla DeepSpeech'


class PicovoiceCheetahASREngine(Engine):
    def __init__(self, lm='language_model.pv'):
        cheetah_dir = os.path.join(os.path.dirname(__file__), 'res/cheetah')
        self._cheetah_demo_path = os.path.join(cheetah_dir, 'cheetah_demo')
        self._cheetah_library_path = os.path.join(cheetah_dir, 'libpv_cheetah.so')
        self._cheetah_acoustic_model_path = os.path.join(cheetah_dir, 'acoustic_model.pv')
        self._cheetah_language_model_path = os.path.join(cheetah_dir, lm)
        self._cheetah_license_path = os.path.join(cheetah_dir, 'cheetah_eval_linux.lic')

    def transcribe(self, path):
        args = [
            self._cheetah_demo_path,
            self._cheetah_library_path,
            self._cheetah_acoustic_model_path,
            self._cheetah_language_model_path,
            self._cheetah_license_path,
            path]
        res = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')

        # Remove license notice
        filtered_res = [x for x in res.split('\n') if '[' not in x]
        filtered_res = '\n'.join(filtered_res)

        return filtered_res.strip('\n ')

    def __str__(self):
        return 'Picovoice Cheetah'


class PicovoiceLeopardASREngine(Engine):
    def __init__(self, lm='language_model.pv'):
        leopard_dir = os.path.join(os.path.dirname(__file__), 'res/leopard')
        self._demo_path = os.path.join(leopard_dir, 'leopard_demo')
        self._library_path = os.path.join(leopard_dir, 'libpv_leopard.so')
        self._acoustic_model_path = os.path.join(leopard_dir, 'acoustic_model.pv')
        self._language_model_path = os.path.join(leopard_dir, lm)
        self._license_path = os.path.join(leopard_dir, 'leopard_eval_linux.lic')

    def transcribe(self, path):
        args = [
            self._demo_path,
            self._library_path,
            self._acoustic_model_path,
            self._language_model_path,
            self._license_path,
            path]
        res = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')

        # Remove license notice
        filtered_res = [x for x in res.split('\n') if '[' not in x]
        filtered_res = '\n'.join(filtered_res)

        return filtered_res.strip('\n ')

    def __str__(self):
        return 'Picovoice Leopard'


__all__ = ['Engines', 'Engine']
