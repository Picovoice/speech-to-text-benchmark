import json
import os
import time
import uuid
import warnings
from enum import Enum
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
import boto3
import pvcheetah
import pvleopard
import requests
import soundfile
import torch
import whisper
from google.cloud import speech
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1

from languages import (
    LANGUAGE_TO_CODE,
    Languages
)

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="Performing inference on CPU when CUDA is available")

NUM_THREADS = 1
os.environ["OMP_NUM_THREADS"] = str(NUM_THREADS)
os.environ["MKL_NUM_THREADS"] = str(NUM_THREADS)
torch.set_num_threads(NUM_THREADS)
torch.set_num_interop_threads(NUM_THREADS)


class Engines(Enum):
    AMAZON_TRANSCRIBE = "AMAZON_TRANSCRIBE"
    AZURE_SPEECH_TO_TEXT = "AZURE_SPEECH_TO_TEXT"
    GOOGLE_SPEECH_TO_TEXT = "GOOGLE_SPEECH_TO_TEXT"
    GOOGLE_SPEECH_TO_TEXT_ENHANCED = "GOOGLE_SPEECH_TO_TEXT_ENHANCED"
    IBM_WATSON_SPEECH_TO_TEXT = "IBM_WATSON_SPEECH_TO_TEXT"
    WHISPER_TINY = "WHISPER_TINY"
    WHISPER_BASE = "WHISPER_BASE"
    WHISPER_SMALL = "WHISPER_SMALL"
    WHISPER_MEDIUM = "WHISPER_MEDIUM"
    WHISPER_LARGE = "WHISPER_LARGE"
    WHISPER_LARGE_V2 = "WHISPER_LARGE_V2"
    WHISPER_LARGE_V3 = "WHISPER_LARGE_V3"
    PICOVOICE_CHEETAH = "PICOVOICE_CHEETAH"
    PICOVOICE_LEOPARD = "PICOVOICE_LEOPARD"


class Engine(object):
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    def audio_sec(self) -> float:
        raise NotImplementedError()

    def process_sec(self) -> float:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, x: Engines, language: Languages, **kwargs):
        if x is Engines.AMAZON_TRANSCRIBE:
            return AmazonTranscribeEngine(language=language)
        elif x is Engines.AZURE_SPEECH_TO_TEXT:
            return AzureSpeechToTextEngine(language=language, **kwargs)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToTextEngine(language=language)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED:
            return GoogleSpeechToTextEnhancedEngine(language=language)
        elif x is Engines.WHISPER_TINY:
            return WhisperTiny(language=language)
        elif x is Engines.WHISPER_BASE:
            return WhisperBase(language=language)
        elif x is Engines.WHISPER_SMALL:
            return WhisperSmall(language=language)
        elif x is Engines.WHISPER_MEDIUM:
            return WhisperMedium(language=language)
        elif x is Engines.WHISPER_LARGE:
            return WhisperLarge(language=language)
        elif x is Engines.WHISPER_LARGE_V2:
            return WhisperLargeV2(language=language)
        elif x is Engines.WHISPER_LARGE_V3:
            return WhisperLargeV3(language=language)
        elif x is Engines.PICOVOICE_CHEETAH:
            return PicovoiceCheetahEngine(**kwargs)
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardEngine(**kwargs)
        elif x is Engines.IBM_WATSON_SPEECH_TO_TEXT:
            return IBMWatsonSpeechToTextEngine(language=language, **kwargs)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


class AmazonTranscribeEngine(Engine):
    def __init__(self, language: Languages):
        self._language_code = LANGUAGE_TO_CODE[language]

        self._s3_client = boto3.client("s3")
        self._s3_bucket = str(uuid.uuid4())
        self._s3_client.create_bucket(
            ACL="private",
            Bucket=self._s3_bucket,
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
        )

        self._transcribe_client = boto3.client("transcribe")

    def transcribe(self, path: str) -> str:
        cache_path = path.replace(".flac", ".aws")

        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res

        job_name = str(uuid.uuid4())
        s3_object = os.path.basename(path)
        self._s3_client.upload_file(path, self._s3_bucket, s3_object)

        self._transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": f"https://s3-us-west-2.amazonaws.com/{self._s3_bucket}/{s3_object}"},
            MediaFormat="flac",
            LanguageCode=self._language_code,
        )

        while True:
            status = self._transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
            if job_status == "COMPLETED":
                break
            elif job_status == "FAILED":
                error = status["TranscriptionJob"].get("FailureReason", "Unknown error")
                raise RuntimeError(f"Amazon Transcribe job {job_name} failed: {error}")
            time.sleep(1)

        content = requests.get(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])

        res = json.loads(content.content.decode("utf8"))["results"]["transcripts"][0]["transcript"]

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        response = self._s3_client.list_objects_v2(Bucket=self._s3_bucket)
        while response["KeyCount"] > 0:
            self._s3_client.delete_objects(
                Bucket=self._s3_bucket,
                Delete={"Objects": [{"Key": obj["Key"]} for obj in response["Contents"]]},
            )
            response = self._s3_client.list_objects_v2(Bucket=self._s3_bucket)

        self._s3_client.delete_bucket(Bucket=self._s3_bucket)

    def __str__(self):
        return "Amazon Transcribe"


class AzureSpeechToTextEngine(Engine):
    def __init__(
        self,
        azure_speech_key: str,
        azure_speech_location: str,
        language: Languages,
    ):
        self._language_code = LANGUAGE_TO_CODE[language]
        self._azure_speech_key = azure_speech_key
        self._azure_speech_location = azure_speech_location

    def transcribe(self, path: str) -> str:
        cache_path = path.replace(".flac", ".ms")

        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                res = f.read()
            return res

        wav_path = path.replace(".flac", ".wav")
        soundfile.write(
            wav_path,
            soundfile.read(path, dtype="int16")[0],
            samplerate=16000,
        )

        speech_config = speechsdk.SpeechConfig(
            subscription=self._azure_speech_key,
            region=self._azure_speech_location,
            speech_recognition_language=self._language_code,
        )
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        res = ""

        def recognized_cb(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                nonlocal res
                res += " " + evt.result.text

        done = False

        def stop_cb(_):
            nonlocal done
            done = True

        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(0.5)

        speech_recognizer.stop_continuous_recognition()

        os.remove(wav_path)

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "Microsoft Azure Speech-to-text"


class GoogleSpeechToTextEngine(Engine):
    def __init__(
        self,
        language: Languages,
        cache_extension: str = ".ggl",
        model: Optional[str] = None,
    ):
        self._language_code = LANGUAGE_TO_CODE[language]

        self._client = speech.SpeechClient()

        self._config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16000,
            language_code=self._language_code,
            model=model,
            enable_automatic_punctuation=True,
        )

        self._cache_extension = cache_extension

    def transcribe(self, path: str) -> str:
        cache_path = path.replace(".flac", self._cache_extension)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res

        with open(path, "rb") as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)

        response = self._client.recognize(config=self._config, audio=audio)

        res = " ".join(result.alternatives[0].transcript for result in response.results)

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "Google Speech-to-Text"


class GoogleSpeechToTextEnhancedEngine(GoogleSpeechToTextEngine):
    def __init__(self, language: Languages):
        if language != Languages.EN:
            raise ValueError("GOOGLE_SPEECH_TO_TEXT_ENHANCED engine only supports EN language")
        super().__init__(language=language, cache_extension=".ggle", model="video")

    def __str__(self) -> str:
        return "Google Speech-to-Text Enhanced"


class IBMWatsonSpeechToTextEngine(Engine):
    def __init__(
        self,
        watson_speech_to_text_api_key: str,
        watson_speech_to_text_url: str,
        language: Languages,
    ):
        if language != Languages.EN:
            raise ValueError("IBM_WATSON_SPEECH_TO_TEXT engine only supports EN language")

        self._service = SpeechToTextV1(authenticator=IAMAuthenticator(watson_speech_to_text_api_key))
        self._service.set_service_url(watson_speech_to_text_url)

    def transcribe(self, path: str) -> str:
        cache_path = path.replace(".flac", ".ibm")
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                res = f.read()
            return res

        with open(path, "rb") as f:
            response = self._service.recognize(
                audio=f,
                content_type="audio/flac",
                smart_formatting=True,
                end_of_phrase_silence_time=15,
            ).get_result()

        res = ""
        if response and ("results" in response) and response["results"]:
            res = response["results"][0]["alternatives"][0]["transcript"]

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "IBM Watson Speech-to-Text"


class Whisper(Engine):
    SAMPLE_RATE = 16000

    LANGUAGE_TO_WHISPER_CODE = {
        Languages.EN: "en",
        Languages.DE: "de",
        Languages.ES: "es",
        Languages.FR: "fr",
        Languages.IT: "it",
        Languages.PT_PT: "pt",
        Languages.PT_BR: "pt",
    }

    def __init__(self, cache_extension: str, model: str, language: Languages):
        self._model = whisper.load_model(model, device="cpu")
        self._cache_extension = cache_extension
        self._language_code = self.LANGUAGE_TO_WHISPER_CODE[language]
        self._audio_sec = 0.0
        self._proc_sec = 0.0

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype="int16")
        assert sample_rate == self.SAMPLE_RATE
        self._audio_sec += audio.size / sample_rate

        cache_path = path.replace(".flac", self._cache_extension)
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res

        start_sec = time.time()
        res = self._model.transcribe(path, language=self._language_code)["text"]
        self._proc_sec += time.time() - start_sec

        with open(cache_path, "w") as f:
            f.write(res)

        return res

    def audio_sec(self) -> float:
        return self._audio_sec

    def process_sec(self) -> float:
        return self._proc_sec

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        raise NotImplementedError()


class WhisperTiny(Whisper):
    def __init__(self, language: Languages):
        model = "tiny.en" if language == Languages.EN else "tiny"
        super().__init__(cache_extension=".wspt", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Tiny"


class WhisperBase(Whisper):
    def __init__(self, language: Languages):
        model = "base.en" if language == Languages.EN else "base"
        super().__init__(cache_extension=".wspb", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Base"


class WhisperSmall(Whisper):
    def __init__(self, language: Languages):
        model = "small.en" if language == Languages.EN else "small"
        super().__init__(cache_extension=".wsps", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Small"


class WhisperMedium(Whisper):
    def __init__(self, language: Languages):
        model = "medium.en" if language == Languages.EN else "medium"
        super().__init__(cache_extension=".wspm", model=model, language=language)

    def __str__(self) -> str:
        return "Whisper Medium"


class WhisperLarge(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl", model="large-v1", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v1"


class WhisperLargeV2(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl2", model="large-v2", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v2"


class WhisperLargeV3(Whisper):
    def __init__(self, language: Languages):
        super().__init__(cache_extension=".wspl3", model="large-v3", language=language)

    def __str__(self) -> str:
        return "Whisper Large-v3"


class PicovoiceCheetahEngine(Engine):
    def __init__(
        self,
        access_key: str,
        model_path: Optional[str],
        library_path: Optional[str],
        punctuation: bool = False,
    ):
        self._cheetah = pvcheetah.create(
            access_key=access_key,
            model_path=model_path,
            library_path=library_path,
            enable_automatic_punctuation=punctuation,
        )
        self._audio_sec = 0.0
        self._proc_sec = 0.0

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype="int16")
        assert sample_rate == self._cheetah.sample_rate
        self._audio_sec += audio.size / sample_rate

        start_sec = time.time()
        res = ""
        for i in range(audio.size // self._cheetah.frame_length):
            partial, _ = self._cheetah.process(
                audio[i * self._cheetah.frame_length : (i + 1) * self._cheetah.frame_length]
            )
            res += partial
        res += self._cheetah.flush()
        self._proc_sec += time.time() - start_sec

        return res

    def audio_sec(self) -> float:
        return self._audio_sec

    def process_sec(self) -> float:
        return self._proc_sec

    def delete(self) -> None:
        self._cheetah.delete()

    def __str__(self) -> str:
        return "Picovoice Cheetah"


class PicovoiceLeopardEngine(Engine):
    def __init__(
        self,
        access_key: str,
        model_path: Optional[str],
        library_path: Optional[str],
        punctuation: bool = False,
    ):
        self._leopard = pvleopard.create(
            access_key=access_key,
            model_path=model_path,
            library_path=library_path,
            enable_automatic_punctuation=punctuation,
        )
        self._audio_sec = 0.0
        self._proc_sec = 0.0

    def transcribe(self, path: str) -> str:
        audio, sample_rate = soundfile.read(path, dtype="int16")
        assert sample_rate == self._leopard.sample_rate
        self._audio_sec += audio.size / sample_rate

        start_sec = time.time()
        res = self._leopard.process(audio)
        self._proc_sec += time.time() - start_sec

        return res[0]

    def audio_sec(self) -> float:
        return self._audio_sec

    def process_sec(self) -> float:
        return self._proc_sec

    def delete(self) -> None:
        self._leopard.delete()

    def __str__(self):
        return "Picovoice Leopard"


__all__ = [
    "Engine",
    "Engines",
]
