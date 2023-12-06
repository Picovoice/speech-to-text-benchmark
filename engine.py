import json
import os
import string
import time
import uuid
from enum import Enum

import azure.cognitiveservices.speech as speechsdk
import boto3
import inflect
import pvcheetah
import pvleopard
import requests
import soundfile
import whisper
from google.cloud import speech
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1


class Engines(Enum):
    AMAZON_TRANSCRIBE = "AMAZON_TRANSCRIBE"
    AZURE_SPEECH_TO_TEXT = 'AZURE_SPEECH_TO_TEXT'
    GOOGLE_SPEECH_TO_TEXT = "GOOGLE_SPEECH_TO_TEXT"
    GOOGLE_SPEECH_TO_TEXT_ENHANCED = "GOOGLE_SPEECH_TO_TEXT_ENHANCED"
    IBM_WATSON_SPEECH_TO_TEXT = "IBM_WATSON_SPEECH_TO_TEXT"
    WHISPER_TINY = "WHISPER_TINY"
    WHISPER_SMALL = "WHISPER_SMALL"
    PICOVOICE_CHEETAH = "PICOVOICE_CHEETAH"
    PICOVOICE_LEOPARD = "PICOVOICE_LEOPARD"


class Engine(object):
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def rtf(self) -> float:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x, **kwargs):
        if x is Engines.AMAZON_TRANSCRIBE:
            return AmazonTranscribeEngine()
        elif x is Engines.AZURE_SPEECH_TO_TEXT:
            return AzureSpeechToTextEngine(**kwargs)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToTextEngine()
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED:
            return GoogleSpeechToTextEnhancedEngine()
        elif x is Engines.WHISPER_TINY:
            return WhisperTiny()
        elif x is Engines.WHISPER_SMALL:
            return WhisperSmall()
        elif x is Engines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahEngine(**kwargs)
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardEngine(**kwargs)
        elif x is Engines.IBM_WATSON_SPEECH_TO_TEXT:
            return IBMWatsonSpeechToTextEngine(**kwargs)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")

    @staticmethod
    def _normalize(text: str) -> str:
        p = inflect.engine()
        text = text.translate(str.maketrans('', '', string.punctuation.replace("'", "").replace("-", ""))).lower()
        text = text.replace("-", " ")

        def num2txt(y):
            return p.number_to_words(y).replace('-', ' ').replace(',', '') if any(c.isdigit() for c in y) else y

        return ' '.join(num2txt(x) for x in text.split())


class AmazonTranscribeEngine(Engine):
    def __init__(self):
        self._s3_client = boto3.client('s3')
        self._s3_bucket = str(uuid.uuid4())
        self._s3_client.create_bucket(
            ACL='private',
            Bucket=self._s3_bucket,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )

        self._transcribe_client = boto3.client('transcribe')

    def transcribe(self, path: str) -> str:
        cache_path = path.replace('.flac', '.aws')

        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return self._normalize(res)

        job_name = str(uuid.uuid4())
        s3_object = os.path.basename(path)
        self._s3_client.upload_file(path, self._s3_bucket, s3_object)

        self._transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f'https://s3-us-west-2.amazonaws.com/{self._s3_bucket}/{s3_object}'},
            MediaFormat='flac',
            LanguageCode='en-US')

        while True:
            status = self._transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                break
            time.sleep(1)

        content = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])

        res = json.loads(content.content.decode('utf8'))['results']['transcripts'][0]['transcript']

        with open(cache_path, 'w') as f:
            f.write(res)

        res = self._normalize(res)

        return res

    def rtf(self) -> float:
        return -1.

    def delete(self) -> None:
        response = self._s3_client.list_objects_v2(Bucket=self._s3_bucket)
        while response['KeyCount'] > 0:
            self._s3_client.delete_objects(
                Bucket=self._s3_bucket,
                Delete={'Objects': [{'Key': obj['Key']} for obj in response['Contents']]}
            )
            response = self._s3_client.list_objects_v2(Bucket=self._s3_bucket)

        self._s3_client.delete_bucket(Bucket=self._s3_bucket)

    def __str__(self):
        return 'Amazon Transcribe'


class AzureSpeechToTextEngine(Engine):
    def __init__(self, azure_speech_key: str, azure_speech_location: str):
        self._azure_speech_key = azure_speech_key
        self._azure_speech_location = azure_speech_location

    def transcribe(self, path: str) -> str:
        cache_path = path.replace('.flac', '.ms')

        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                res = f.read()
            return self._normalize(res)

        wav_path = path.replace('.flac', '.wav')
        soundfile.write(wav_path, soundfile.read(path, dtype='int16')[0], samplerate=16000)

        speech_config = speechsdk.SpeechConfig(subscription=self._azure_speech_key, region=self._azure_speech_location)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        result = speech_recognizer.recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.NoMatch:
            raise RuntimeError(f"No speech could be recognized: {result.no_match_details}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error: {cancellation_details.error_details}")
            raise RuntimeError(f"Speech Recognition canceled: {cancellation_details.reason}")

        res = result.text
        os.remove(wav_path)

        with open(cache_path, 'w') as f:
            f.write(res)

        res = self._normalize(res)

        return res

    def rtf(self) -> float:
        return -1

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Microsoft Azure Speech-to-text'


class GoogleSpeechToTextEngine(Engine):
    def __init__(self, cache_extension: str = '.ggl', model: str = None):
        self._client = speech.SpeechClient()

        self._config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16000,
            language_code="en-US",
            model=model
        )

        self._cache_extension = cache_extension

    def transcribe(self, path: str) -> str:
        cache_path = path.replace('.flac', self._cache_extension)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return self._normalize(res)

        with open(path, 'rb') as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)

        response = self._client.recognize(config=self._config, audio=audio)

        res = ' '.join(result.alternatives[0].transcript for result in response.results)

        with open(cache_path, 'w') as f:
            f.write(res)

        res = self._normalize(res)

        return res

    def rtf(self) -> float:
        return -1.

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Google Speech-to-Text'


class GoogleSpeechToTextEnhancedEngine(GoogleSpeechToTextEngine):
    def __init__(self):
        super().__init__(cache_extension='.ggle', model="video")

    def __str__(self) -> str:
        return 'Google Speech-to-Text Enhanced'


class IBMWatsonSpeechToTextEngine(Engine):
    def __init__(self, watson_speech_to_text_api_key: str, watson_speech_to_text_url: str):
        self._service = SpeechToTextV1(authenticator=IAMAuthenticator(watson_speech_to_text_api_key))
        self._service.set_service_url(watson_speech_to_text_url)

    def transcribe(self, path: str) -> str:
        cache_path = path.replace('.flac', '.ibm')
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                res = f.read()
            return self._normalize(res)

        with open(path, 'rb') as f:
            response = self._service.recognize(
                audio=f,
                content_type='audio/flac',
                smart_formatting=True,
                end_of_phrase_silence_time=15,
            ).get_result()

        res = ''
        if response and ('results' in response) and response['results']:
            res = response['results'][0]['alternatives'][0]['transcript']

        with open(cache_path, 'w') as f:
            f.write(res)

        res = self._normalize(res)

        return res

    def rtf(self) -> float:
        return -1

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return 'IBM Watson Speech-to-Text'


class WhisperTiny(Engine):
    SAMPLE_RATE = 16000

    def __init__(self, cache_extension: str = ".wspt", model: str = "tiny.en"):
        self._model = whisper.load_model(model, device="cpu")
        self._cache_extension = cache_extension
        self._audio_sec = 0.
        self._proc_sec = 0.

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype='int16')
        assert sample_rate == self.SAMPLE_RATE
        self._audio_sec += audio.size / sample_rate

        cache_path = path.replace('.flac', self._cache_extension)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return self._normalize(res)

        start_sec = time.time()
        res = self._model.transcribe(path)['text']
        self._proc_sec += time.time() - start_sec

        with open(cache_path, 'w') as f:
            f.write(res)

        res = self._normalize(res)

        return res

    def rtf(self) -> float:
        return self._proc_sec / self._audio_sec

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Whisper Tiny'


class WhisperSmall(WhisperTiny):
    def __init__(self):
        super().__init__(cache_extension='.wsps', model="small.en")

    def __str__(self) -> str:
        return 'Whisper Small'


class PicovoiceCheetahEngine(Engine):
    def __init__(self, access_key: str):
        self._cheetah = pvcheetah.create(access_key=access_key)
        self._audio_sec = 0.
        self._proc_sec = 0.

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype='int16')
        assert sample_rate == self._cheetah.sample_rate
        self._audio_sec += audio.size / sample_rate

        start_sec = time.time()
        res = ''
        for i in range(audio.size // self._cheetah.frame_length):
            partial, _ = \
                self._cheetah.process(audio[i * self._cheetah.frame_length: (i + 1) * self._cheetah.frame_length])
            res += partial
        res += self._cheetah.flush()
        self._proc_sec += time.time() - start_sec

        return res

    def rtf(self) -> float:
        return self._proc_sec / self._audio_sec

    def delete(self) -> None:
        self._cheetah.delete()

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

        return res[0]

    def rtf(self) -> float:
        return self._proc_sec / self._audio_sec

    def delete(self) -> None:
        self._leopard.delete()

    def __str__(self):
        return 'Picovoice Leopard'


__all__ = ['Engines', 'Engine']
