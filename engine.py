import asyncio
import json
import os
import time
import uuid
import warnings
from enum import Enum
from threading import Event
from typing import (
    Any,
    ByteString,
    Generator,
    Optional,
    Sequence,
    Tuple
)

import azure.cognitiveservices.speech as speechsdk
import boto3
import pvcheetah
import pvleopard
import requests
import soundfile
import torch
import whisper
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import (
    TranscriptEvent,
    TranscriptResultStream
)
from azure.cognitiveservices.speech import SpeechRecognitionEventArgs
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

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2


class Engines(Enum):
    AMAZON_TRANSCRIBE = "AMAZON_TRANSCRIBE"
    AMAZON_TRANSCRIBE_STREAMING = "AMAZON_TRANSCRIBE_STREAMING"
    AZURE_SPEECH_TO_TEXT = "AZURE_SPEECH_TO_TEXT"
    AZURE_SPEECH_TO_TEXT_REAL_TIME = "AZURE_SPEECH_TO_TEXT_REAL_TIME"
    GOOGLE_SPEECH_TO_TEXT = "GOOGLE_SPEECH_TO_TEXT"
    GOOGLE_SPEECH_TO_TEXT_STREAMING = "GOOGLE_SPEECH_TO_TEXT_STREAMING"
    GOOGLE_SPEECH_TO_TEXT_ENHANCED = "GOOGLE_SPEECH_TO_TEXT_ENHANCED"
    GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING = "GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING"
    IBM_WATSON_SPEECH_TO_TEXT = "IBM_WATSON_SPEECH_TO_TEXT"
    WHISPER_TINY = "WHISPER_TINY"
    WHISPER_BASE = "WHISPER_BASE"
    WHISPER_SMALL = "WHISPER_SMALL"
    WHISPER_MEDIUM = "WHISPER_MEDIUM"
    WHISPER_LARGE = "WHISPER_LARGE"
    WHISPER_LARGE_V2 = "WHISPER_LARGE_V2"
    WHISPER_LARGE_V3 = "WHISPER_LARGE_V3"
    PICOVOICE_CHEETAH = "PICOVOICE_CHEETAH"
    PICOVOICE_CHEETAH_FAST = "PICOVOICE_CHEETAH_FAST"
    PICOVOICE_LEOPARD = "PICOVOICE_LEOPARD"


StreamingEngines = [
    Engines.AMAZON_TRANSCRIBE_STREAMING,
    Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME,
    Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING,
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING,
    Engines.PICOVOICE_CHEETAH,
    Engines.PICOVOICE_CHEETAH_FAST,
]


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
        if x is Engines.AMAZON_TRANSCRIBE_STREAMING:
            return AmazonTranscribeStreamingEngine(language=language, **kwargs)
        elif x is Engines.AZURE_SPEECH_TO_TEXT:
            return AzureSpeechToTextEngine(language=language, **kwargs)
        elif x is Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME:
            return AzureSpeechToTextRealTimeEngine(language=language, **kwargs)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToTextEngine(language=language)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED:
            return GoogleSpeechToTextEnhancedEngine(language=language)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING:
            return GoogleSpeechToTextStreamingEngine(language=language, **kwargs)
        elif x is Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING:
            return GoogleSpeechToTextEnhancedStreamingEngine(language=language, **kwargs)
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
        elif x is Engines.PICOVOICE_CHEETAH_FAST:
            return PicovoiceCheetahEngine(**kwargs)
        elif x is Engines.PICOVOICE_LEOPARD:
            return PicovoiceLeopardEngine(**kwargs)
        elif x is Engines.IBM_WATSON_SPEECH_TO_TEXT:
            return IBMWatsonSpeechToTextEngine(language=language, **kwargs)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{x}`")


WordLatencyOutputType = Tuple[Sequence[str], Sequence[float], Sequence[float]]


class StreamingEngine(Engine):
    @property
    def is_async(self) -> bool:
        raise NotImplementedError()

    async def _measure_word_latency_async(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        raise NotImplementedError()

    def _measure_word_latency(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        raise NotImplementedError()

    def measure_word_latency(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        if self.is_async:
            return asyncio.run(self._measure_word_latency_async(path, alignments))
        else:
            return self._measure_word_latency(path, alignments)

    def transcribe(self, path: str) -> str:
        words, _, _ = self.measure_word_latency(path, alignments=None)
        return " ".join(words)

    def get_chunk_size_ms(self) -> int:
        raise NotImplementedError()

    def load_pcm(self, path: str) -> ByteString:
        pcm, sample_rate = soundfile.read(path, dtype="int16")
        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Incorrect sample rate for `{path}`: expected {SAMPLE_RATE} got {sample_rate}")
        return pcm.tobytes()

    def get_chunk_size_bytes(self) -> int:
        chunk_ms = self.get_chunk_size_ms()
        return int((chunk_ms / 1000) * (SAMPLE_RATE * BYTES_PER_SAMPLE))


class AmazonTranscribeEngine(Engine):
    def __init__(self, language: Languages, aws_location: str = "us-west-2"):
        self._language_code = LANGUAGE_TO_CODE[language]

        self._s3_client = boto3.client("s3")
        self._s3_bucket = str(uuid.uuid4())
        self._s3_client.create_bucket(
            ACL="private",
            Bucket=self._s3_bucket,
            CreateBucketConfiguration={"LocationConstraint": aws_location},
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


class AmazonTranscribeStreamingEngine(StreamingEngine):
    def __init__(
        self,
        language: Languages,
        chunk_size_ms: int,
        apply_delay: bool,
        ignore_punctuation: bool,
        aws_location: str = "us-west-2",
    ) -> None:
        super().__init__()
        self._language_code = LANGUAGE_TO_CODE[language]
        self._chunk_size_ms = chunk_size_ms
        self._apply_delay = apply_delay
        self._ignore_punctuation = ignore_punctuation
        self._location = aws_location

        self._client = TranscribeStreamingClient(region=self._location)

    @property
    def is_async(self) -> bool:
        return True

    def get_chunk_size_ms(self) -> int:
        return self._chunk_size_ms

    async def _measure_word_latency_async(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        cache_path = path.replace(".flac", ".awsrt")

        if alignments is None and os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res.split(), [], []

        stream = await self._client.start_stream_transcription(
            language_code=self._language_code,
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )

        handler = AmazonTranscribeStreamingHandler(stream.output_stream, ignore_punctuation=self._ignore_punctuation)
        send_timings = []

        async def write_chunks():
            current_audio_time = 0.0
            word_timings = [aln[-1] for aln in alignments] if alignments is not None else []
            pcm = self.load_pcm(path)

            total_bytes = len(pcm)
            current_byte = 0
            chunk_size_bytes = self.get_chunk_size_bytes()

            while current_byte < total_bytes:
                chunk = pcm[current_byte : current_byte + chunk_size_bytes]
                chunk_end_time = current_audio_time + (self._chunk_size_ms / 1000)

                send_time = time.time()
                await stream.input_stream.send_audio_event(audio_chunk=chunk)

                for word_time in word_timings:
                    if current_audio_time < word_time <= chunk_end_time:
                        send_timings.append(send_time)

                if self._apply_delay:
                    await asyncio.sleep(self._chunk_size_ms / 1000)

                current_audio_time = chunk_end_time
                current_byte += chunk_size_bytes

            await stream.input_stream.end_stream()

        await asyncio.gather(write_chunks(), handler.handle_events())

        if alignments is None:
            with open(cache_path, "w") as f:
                f.write(" ".join(handler._emitted_words))

        return handler._emitted_words, handler._receive_timings, send_timings

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "Amazon Transcribe Streaming"


class AmazonTranscribeStreamingHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream: TranscriptResultStream, ignore_punctuation: bool) -> None:
        super().__init__(transcript_result_stream)
        self._emitted_words = []
        self._receive_timings = []
        self._last_word_index = 0

        self._ignore_punctuation = ignore_punctuation
        self._punctuation_trans = str.maketrans({".": "", ",": "", "?": ""})

    async def handle_transcript_event(self, transcript_event: TranscriptEvent) -> None:
        current_time = time.time()

        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives:
                for alt in result.alternatives:
                    if alt.transcript:
                        if self._ignore_punctuation:
                            words = alt.transcript.translate(self._punctuation_trans).split()
                        else:
                            words = alt.transcript.split()

                        partial_transcript_reset = len(words) < self._last_word_index
                        if partial_transcript_reset:
                            self._last_word_index = 0

                        if self._last_word_index > 0:
                            last_emitted_word_changed = self._emitted_words[-1] != words[self._last_word_index - 1]
                            if last_emitted_word_changed:
                                self._emitted_words[-1] = words[self._last_word_index - 1]
                                self._receive_timings[-1] = current_time

                        if len(words) > self._last_word_index:
                            new_words = words[self._last_word_index :]
                            for word in new_words:
                                self._emitted_words.append(word)
                                self._receive_timings.append(current_time)

                            self._last_word_index = len(words)


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
            samplerate=SAMPLE_RATE,
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


class AzureSpeechToTextRealTimeEngine(StreamingEngine):
    def __init__(
        self,
        language: Languages,
        chunk_size_ms: int,
        apply_delay: bool,
        ignore_punctuation: bool,
        azure_speech_key: str,
        azure_speech_location: str,
    ) -> None:
        super().__init__()
        self._language_code = LANGUAGE_TO_CODE[language]
        self._chunk_size_ms = chunk_size_ms
        self._apply_delay = apply_delay
        self._ignore_punctuation = ignore_punctuation
        self._azure_speech_key = azure_speech_key
        self._azure_speech_location = azure_speech_location


    @property
    def is_async(self) -> bool:
        return True

    def get_chunk_size_ms(self) -> int:
        return self._chunk_size_ms

    async def _measure_word_latency_async(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        cache_path = path.replace(".flac", ".msrt")

        if alignments is None and os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                res = f.read()
            return res.split(), [], []

        speech_config = speechsdk.SpeechConfig(
            subscription=self._azure_speech_key,
            region=self._azure_speech_location,
            speech_recognition_language=self._language_code,
        )

        audio_format = speechsdk.audio.AudioStreamFormat(samples_per_second=SAMPLE_RATE)
        push_stream = speechsdk.audio.PushAudioInputStream(audio_format)
        audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        handler = AzureSpeechToTextRealTimeHandler(ignore_punctuation=self._ignore_punctuation)
        speech_recognizer.recognizing.connect(handler.recognizing_cb)
        speech_recognizer.recognized.connect(handler.recognized_cb)
        speech_recognizer.session_stopped.connect(handler.session_stopped_cb)
        speech_recognizer.canceled.connect(handler.canceled_cb)

        send_timings = []

        async def write_chunks() -> None:
            current_audio_time = 0.0
            word_timings = [aln[-1] for aln in alignments] if alignments is not None else []
            pcm = self.load_pcm(path)

            total_bytes = len(pcm)
            current_byte = 0
            chunk_size_bytes = self.get_chunk_size_bytes()

            while current_byte < total_bytes:
                chunk = pcm[current_byte : current_byte + chunk_size_bytes]
                chunk_end_time = current_audio_time + (self._chunk_size_ms / 1000)

                send_time = time.time()
                push_stream.write(chunk)

                for word_time in word_timings:
                    if current_audio_time < word_time <= chunk_end_time:
                        send_timings.append(send_time)

                if self._apply_delay:
                    await asyncio.sleep(self._chunk_size_ms / 1000)

                current_audio_time = chunk_end_time
                current_byte += chunk_size_bytes

            push_stream.close()

        speech_recognizer.start_continuous_recognition_async()
        await write_chunks()

        await asyncio.get_event_loop().run_in_executor(None, handler._done_event.wait, 10)

        speech_recognizer.stop_continuous_recognition_async()

        if alignments is None:
            with open(cache_path, "w") as f:
                f.write(" ".join(handler._emitted_words))

        return handler._emitted_words, handler._receive_timings, send_timings

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "Microsoft Azure Speech-to-text Real-time"


class AzureSpeechToTextRealTimeHandler:
    def __init__(self, ignore_punctuation: bool) -> None:
        self._emitted_words = []
        self._receive_timings = []
        self._last_word_index = 0
        self._done_event = Event()

        self._ignore_punctuation = ignore_punctuation
        self._punctuation_trans = str.maketrans({".": "", ",": "", "?": ""})

    def _recognize_helper(self, evt: SpeechRecognitionEventArgs) -> None:
        current_time = time.time()
        if self._ignore_punctuation:
            words = evt.result.text.translate(self._punctuation_trans).split()
        else:
            words = evt.result.text.split()

        partial_transcript_reset = len(words) < self._last_word_index
        if partial_transcript_reset:
            self._last_word_index = 0

        if self._last_word_index > 0:
            last_emitted_word_changed = self._emitted_words[-1] != words[self._last_word_index - 1]
            if last_emitted_word_changed:
                self._emitted_words[-1] = words[self._last_word_index - 1]
                self._receive_timings[-1] = current_time

        if len(words) > self._last_word_index:
            new_words = words[self._last_word_index :]
            for word in new_words:
                self._emitted_words.append(word)
                self._receive_timings.append(current_time)

            self._last_word_index = len(words)

    def recognized_cb(self, evt: SpeechRecognitionEventArgs) -> None:
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if evt.result.text:
                self._recognize_helper(evt)

    def recognizing_cb(self, evt: SpeechRecognitionEventArgs) -> None:
        if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            if evt.result.text:
                self._recognize_helper(evt)

    def session_stopped_cb(self, evt: SpeechRecognitionEventArgs) -> None:
        self._done_event.set()

    def canceled_cb(self, evt: SpeechRecognitionEventArgs) -> None:
        self._done_event.set()


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
            sample_rate_hertz=SAMPLE_RATE,
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


class GoogleSpeechToTextStreamingEngine(StreamingEngine):
    def __init__(
        self,
        language: Languages,
        chunk_size_ms: int,
        apply_delay: bool,
        ignore_punctuation: bool,
        cache_extension: str = ".gglrt",
        model: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._language_code = LANGUAGE_TO_CODE[language]
        self._chunk_size_ms = chunk_size_ms
        self._apply_delay = apply_delay
        self._ignore_punctuation = ignore_punctuation
        self._cache_extension = cache_extension

        self._client = speech.SpeechClient()

        self._config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=self._language_code,
            model=model,
            enable_automatic_punctuation=True,
        )

        self._streaming_config = speech.StreamingRecognitionConfig(
            config=self._config, interim_results=True, single_utterance=False
        )

    @property
    def is_async(self) -> bool:
        return False

    def get_chunk_size_ms(self) -> int:
        return self._chunk_size_ms

    def _measure_word_latency(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        cache_path = path.replace(".flac", self._cache_extension)
        if alignments is None and os.path.exists(cache_path):
            with open(cache_path) as f:
                res = f.read()
            return res.split(), [], []

        word_timings = [aln[-1] for aln in alignments] if alignments is not None else []
        pcm = self.load_pcm(path)

        streamer = GoogleSpeechToTextStreamingAudioGenerator(
            pcm=pcm,
            word_timings=word_timings,
            chunk_size_bytes=self.get_chunk_size_bytes(),
            chunk_size_ms=self._chunk_size_ms,
            apply_delay=self._apply_delay,
        )
        handler = GoogleSpeechToTextStreamingHandler(ignore_punctuation=self._ignore_punctuation)

        def request_generator():
            yield from streamer.stream_generator()

        responses = self._client.streaming_recognize(config=self._streaming_config, requests=request_generator())

        for response in responses:
            if len(response.results) == 0:
                continue

            if response.results[0].is_final or len(response.results) == 2:
                handler._process_result(response.results[0])

        streamer.stop()

        if alignments is None:
            with open(cache_path, "w") as f:
                f.write(" ".join(handler._emitted_words))

        return handler._emitted_words, handler._receive_timings, streamer._send_timings

    def audio_sec(self) -> float:
        return -1.0

    def process_sec(self) -> float:
        return -1.0

    def delete(self) -> None:
        pass

    def __str__(self) -> str:
        return "Google Speech-to-Text Streaming"


class GoogleSpeechToTextEnhancedStreamingEngine(GoogleSpeechToTextStreamingEngine):
    def __init__(
        self,
        language: Languages,
        chunk_size_ms: int,
        apply_delay: bool,
        ignore_punctuation: bool,
    ) -> None:
        if language != Languages.EN:
            raise ValueError("GOOGLE_SPEECH_TO_TEXT_ENHANCED_STREAMING engine only supports EN language")
        super().__init__(
            chunk_size_ms=chunk_size_ms,
            apply_delay=apply_delay,
            ignore_punctuation=ignore_punctuation,
            language=language,
            cache_extension=".gglert",
            model="video",
        )

    def __str__(self) -> str:
        return "Google Speech-to-Text Enhanced Streaming"


class GoogleSpeechToTextStreamingAudioGenerator(object):
    def __init__(
        self,
        pcm: ByteString,
        word_timings: Sequence[float],
        chunk_size_bytes: int,
        chunk_size_ms: int,
        apply_delay: bool,
    ) -> None:
        self._pcm = pcm
        self._word_timings = word_timings
        self._chunk_size_bytes = chunk_size_bytes
        self._chunk_size_ms = chunk_size_ms
        self._apply_delay = apply_delay

        self._send_timings = []
        self._finished = False

    def stream_generator(self) -> Generator[speech.StreamingRecognizeRequest, Any, Any]:
        total_bytes = len(self._pcm)
        current_byte = 0
        current_audio_time = 0.0

        while current_byte < total_bytes and not self._finished:
            chunk = self._pcm[current_byte : current_byte + self._chunk_size_bytes]
            chunk_end_time = current_audio_time + (self._chunk_size_ms / 1000)

            send_time = time.time()

            yield speech.StreamingRecognizeRequest(audio_content=chunk)

            for word_time in self._word_timings:
                if current_audio_time < word_time <= chunk_end_time:
                    self._send_timings.append(send_time)

            if self._apply_delay:
                time.sleep(self._chunk_size_ms / 1000)

            current_audio_time = chunk_end_time
            current_byte += self._chunk_size_bytes

    def stop(self) -> None:
        self._finished = True


class GoogleSpeechToTextStreamingHandler(object):
    def __init__(self, ignore_punctuation: bool) -> None:
        self._emitted_words = []
        self._receive_timings = []
        self._last_word_index = 0

        self._ignore_punctuation = ignore_punctuation
        self._punctuation_trans = str.maketrans({".": "", ",": "", "?": ""})

    def _process_result(self, result) -> None:
        current_time = time.time()

        if not result.alternatives:
            return

        transcript = result.alternatives[0].transcript
        if not transcript:
            return

        if self._ignore_punctuation:
            words = transcript.translate(self._punctuation_trans).split()
        else:
            words = transcript.split()

        partial_transcript_reset = len(words) < self._last_word_index
        if partial_transcript_reset:
            self._last_word_index = 0

        if self._last_word_index > 0:
            last_emitted_word_changed = self._emitted_words[-1] != words[self._last_word_index - 1]
            if last_emitted_word_changed:
                self._emitted_words[-1] = words[self._last_word_index - 1]
                self._receive_timings[-1] = current_time

        if len(words) > self._last_word_index:
            new_words = words[self._last_word_index :]
            for word in new_words:
                self._emitted_words.append(word)
                self._receive_timings.append(current_time)

            self._last_word_index = len(words)


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
        assert sample_rate == SAMPLE_RATE
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


class PicovoiceCheetahEngine(StreamingEngine):
    def __init__(
        self,
        access_key: str,
        model_path: Optional[str],
        library_path: Optional[str],
        device: str = "cpu:1",
        punctuation: bool = False,
    ):
        self._cheetah = pvcheetah.create(
            access_key=access_key,
            model_path=model_path,
            device=device,
            library_path=library_path,
            enable_automatic_punctuation=punctuation,
        )
        self._audio_sec = 0.0
        self._proc_sec = 0.0

    @property
    def is_async(self) -> bool:
        return False

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

    def _measure_word_latency(
        self, path: str, alignments: Optional[Sequence[Tuple[float, float]]]
    ) -> WordLatencyOutputType:
        pcm, sample_rate = soundfile.read(path, dtype="int16")
        if sample_rate != SAMPLE_RATE:
            raise ValueError(f"Incorrect sample rate for `{path}`: expected {SAMPLE_RATE} got {sample_rate}")

        send_timings = [aln[-1] for aln in alignments] if alignments is not None else []

        emitted_words = []
        receive_timings = []
        for i in range(pcm.size // self._cheetah.frame_length):
            partial, _ = self._cheetah.process(
                pcm[i * self._cheetah.frame_length : (i + 1) * self._cheetah.frame_length]
            )

            if len(partial) > 0:
                words = partial.split()
                emitted_words.extend(words)

                end_sec = ((i + 1) * self._cheetah.frame_length) / SAMPLE_RATE
                receive_timings.extend([end_sec] * len(words))

        flushed_words = self._cheetah.flush()
        if len(flushed_words) > 0:
            words = flushed_words.split()
            emitted_words.extend(words)
            receive_timings.extend([pcm.size / SAMPLE_RATE] * len(words))

        return emitted_words, receive_timings, send_timings

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
        device: str = "cpu:1",
        punctuation: bool = False,
    ):
        self._leopard = pvleopard.create(
            access_key=access_key,
            model_path=model_path,
            device=device,
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
