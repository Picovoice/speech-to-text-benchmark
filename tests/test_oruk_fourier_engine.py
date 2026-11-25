import importlib
import importlib.machinery
import sys
import types
from pathlib import Path
from unittest import mock

import numpy as np
import pytest
import soundfile

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _ensure_optional_engine_deps() -> None:
    """Stub optional third-party ASR SDKs only when absent in lightweight test envs."""
    stub_modules = [
        "azure",
        "azure.cognitiveservices",
        "azure.cognitiveservices.speech",
        "boto3",
        "pvcheetah",
        "pvleopard",
        "sherpa_onnx",
        "torchaudio",
        "wenet",
        "whisper",
        "amazon_transcribe",
        "amazon_transcribe.client",
        "amazon_transcribe.handlers",
        "amazon_transcribe.model",
        "google",
        "google.cloud",
        "google.cloud.speech",
        "ibm_cloud_sdk_core",
        "ibm_cloud_sdk_core.authenticators",
        "ibm_watson",
        "moonshine_voice",
        "paddlespeech",
        "paddlespeech.cli",
        "paddlespeech.cli.asr",
        "pywhispercpp",
        "pywhispercpp.model",
        "vosk",
        "nemo",
        "nemo.collections",
        "nemo.collections.asr",
        "nemo.collections.asr.parts",
        "nemo.collections.asr.parts.utils",
        "nemo.collections.asr.parts.utils.streaming_utils",
        "editdistance",
        "inflect",
        "num2words",
        "whisper_normalizer",
        "whisper_normalizer.english",
        "whisper_normalizer.basic",
        "zhon",
        "zhon.hanzi",
        "opencc",
        "datasets",
    ]
    for name in stub_modules:
        if name in sys.modules:
            continue
        try:
            importlib.import_module(name)
        except Exception:
            mod = types.ModuleType(name)
            mod.__spec__ = importlib.machinery.ModuleSpec(name, None)
            if name == "amazon_transcribe.handlers":
                mod.TranscriptResultStreamHandler = object
            elif name == "amazon_transcribe.client":
                mod.TranscribeStreamingClient = object
            elif name == "amazon_transcribe.model":
                mod.TranscriptEvent = object
                mod.TranscriptResultStream = object
            elif name == "azure.cognitiveservices.speech":
                mod.SpeechRecognitionEventArgs = object
            elif name == "google.cloud.speech":
                mod.StreamingRecognizeRequest = object
            elif name == "google.cloud":
                pass
            elif name == "ibm_cloud_sdk_core.authenticators":
                mod.IAMAuthenticator = object
            elif name == "ibm_watson":
                mod.SpeechToTextV1 = object
            elif name == "moonshine_voice":
                mod.ModelArch = object
                mod.Transcriber = object
                mod.TranscriptEventListener = object
                mod.get_model_for_language = lambda *a, **kw: None
            elif name == "paddlespeech.cli.asr":
                mod.ASRExecutor = object
            elif name == "pywhispercpp.model":
                mod.Model = object
            elif name == "vosk":
                mod.KaldiRecognizer = object
                mod.Model = object
                mod.SetLogLevel = lambda *a, **kw: None
            elif name == "nemo.collections.asr.parts.utils.streaming_utils":
                mod.CacheAwareStreamingAudioBuffer = object
            sys.modules[name] = mod

    if "google.cloud" in sys.modules and "google.cloud.speech" in sys.modules:
        sys.modules["google.cloud"].speech = sys.modules["google.cloud.speech"]

    if "huggingface_hub" not in sys.modules:
        try:
            importlib.import_module("huggingface_hub")
        except Exception:
            hf_mod = types.ModuleType("huggingface_hub")
            hf_mod.hf_hub_download = lambda *a, **kw: ""
            hf_mod.snapshot_download = lambda *a, **kw: ""
            sys.modules["huggingface_hub"] = hf_mod


_ensure_optional_engine_deps()

import engine  # noqa: E402
from languages import Languages  # noqa: E402


class _FakeBatch(dict):
    def to(self, device, dtype):
        self["moved_to"] = (device, dtype)
        return self


class _FakeProcessor:
    def __init__(self, transcript="hello world"):
        self._transcript = transcript
        self.calls = []

    def apply_transcription_request(self, *, audio, language, return_tensors, processor_kwargs):
        self.calls.append((len(audio), audio[0].shape, language, return_tensors, processor_kwargs))
        import torch

        return _FakeBatch({"input_ids": torch.tensor([[1, 2, 3]])})

    def decode(self, gen_ids, return_format=None):
        assert return_format == "transcription_only"
        return [f"  {self._transcript}  "]


class _FakeModel:
    def __init__(self, dtype):
        self.dtype = dtype
        self.device = None
        self.eval_called = False

    def to(self, device):
        self.device = device
        return self

    def eval(self):
        self.eval_called = True
        return self

    def generate(self, **inputs):
        import torch

        return torch.tensor([[1, 2, 3, 4, 5]])


def _write_flac(path: Path, sr: int = 16000, seconds: float = 1.0, channels: int = 1) -> Path:
    n = int(sr * seconds)
    data = np.zeros((n, channels), dtype=np.float32) if channels > 1 else np.zeros(n, dtype=np.float32)
    soundfile.write(str(path), data, sr, format="FLAC")
    return path


def test_enum_and_non_streaming_registration():
    assert engine.Engines.ORUK_FOURIER_2B.value == "ORUK_FOURIER_2B"
    assert engine.Engines.ORUK_FOURIER_2B_API.value == "ORUK_FOURIER_2B_API"
    assert engine.Engines.ORUK_FOURIER_2B not in engine.StreamingEngines
    assert engine.Engines.ORUK_FOURIER_2B_API not in engine.StreamingEngines


def test_english_only_and_validation_guards():
    with pytest.raises(ValueError, match="only supports EN"):
        engine.Engine.create(engine.Engines.ORUK_FOURIER_2B, language=Languages.DE)
    with pytest.raises(ValueError, match="Unsupported device"):
        engine.Engine.create(engine.Engines.ORUK_FOURIER_2B, language=Languages.EN, device="tpu")
    with pytest.raises(ValueError, match="only supports EN"):
        engine.Engine.create(
            engine.Engines.ORUK_FOURIER_2B_API,
            language=Languages.FR,
            oruk_api_key="dummy-key",
        )
    with pytest.raises(ValueError, match="oruk_api_key"):
        engine.Engine.create(
            engine.Engines.ORUK_FOURIER_2B_API,
            language=Languages.EN,
            oruk_api_key="",
        )
    with pytest.raises(ValueError, match="http:// or https://"):
        engine.Engine.create(
            engine.Engines.ORUK_FOURIER_2B_API,
            language=Languages.EN,
            oruk_api_key="dummy-key",
            oruk_api_url="ftp://invalid.example",
        )


def test_local_engine_green_hf_pin_transcribe_and_cache(tmp_path: Path):
    snap_dir = tmp_path / "snapshot"
    snap_dir.mkdir()
    audio_path = _write_flac(tmp_path / "sample.flac", sr=16000, seconds=1.5, channels=2)

    fake_processor = _FakeProcessor("ask not what your country can do for you")
    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoProcessor = mock.Mock()
    fake_transformers.AutoProcessor.from_pretrained.return_value = fake_processor
    fake_transformers.AutoModelForMultimodalLM = mock.Mock()
    fake_transformers.AutoModelForMultimodalLM.from_pretrained.side_effect = (
        lambda local_dir, local_files_only, dtype: _FakeModel(dtype)
    )

    with (
        mock.patch.dict(sys.modules, {"transformers": fake_transformers}),
        mock.patch.object(engine, "snapshot_download", return_value=str(snap_dir)) as mock_snap,
    ):
        eng = engine.Engine.create(engine.Engines.ORUK_FOURIER_2B, language=Languages.EN, device="cpu")
        assert str(eng) == "Oruk Fourier 2B"
        mock_snap.assert_called_once_with(
            repo_id="oruk/oruk-fourier-2b",
            revision="8c2a8871f1304aa2f634da4fb95e24438c4945b9",
            allow_patterns=list(engine.OrukFourier2BEngine.NATIVE_ROOT_FILES),
            cache_dir=None,
        )
        assert "config.json" in engine.OrukFourier2BEngine.NATIVE_ROOT_FILES
        assert "model.safetensors" in engine.OrukFourier2BEngine.NATIVE_ROOT_FILES

        # First call runs model & writes .oruk cache; stereo is downmixed to mono
        out1 = eng.transcribe(str(audio_path))
        assert out1 == "ask not what your country can do for you"
        assert len(fake_processor.calls) == 1
        assert fake_processor.calls[0][1] == (24000,)
        assert fake_processor.calls[0][2] == ["English"]
        assert eng.audio_sec() == pytest.approx(1.5)
        assert eng.process_sec() >= 0.0
        assert (tmp_path / "sample.oruk").read_text() == out1

        # Second call hits .oruk cache without re-running model
        out2 = eng.transcribe(str(audio_path))
        assert out2 == out1
        assert len(fake_processor.calls) == 1
        assert eng.audio_sec() == pytest.approx(3.0)

        # Wrong sample rate raises ValueError
        bad_audio = _write_flac(tmp_path / "bad_sr.flac", sr=8000, seconds=0.5)
        with pytest.raises(ValueError, match="Incorrect sample rate"):
            eng.transcribe(str(bad_audio))

        eng.delete()
        assert eng._model is None
        assert eng._processor is None


def test_local_engine_raises_clear_error_on_old_transformers(tmp_path: Path):
    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoProcessor = mock.Mock()
    fake_transformers.AutoProcessor.from_pretrained.return_value = object()  # lacks apply_transcription_request
    fake_transformers.AutoModelForMultimodalLM = mock.Mock()

    with (
        mock.patch.dict(sys.modules, {"transformers": fake_transformers}),
        mock.patch.object(engine, "snapshot_download", return_value=str(tmp_path)),
    ):
        with pytest.raises(RuntimeError, match="transformers>=5.21"):
            engine.Engine.create(engine.Engines.ORUK_FOURIER_2B, language=Languages.EN)


def test_api_engine_request_caching_and_error_handling(tmp_path: Path):
    audio_path = _write_flac(tmp_path / "clip.flac", sr=16000, seconds=1.0)
    eng = engine.Engine.create(
        engine.Engines.ORUK_FOURIER_2B_API,
        language=Languages.EN,
        oruk_api_key="test-placeholder-token",
    )
    assert str(eng) == "Oruk Fourier 2B API"
    assert eng.audio_sec() == -1.0
    assert eng.process_sec() == -1.0

    mock_resp = mock.Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"text": "  testing fourier two b  "}

    with mock.patch.object(eng._session, "post", return_value=mock_resp) as mock_post:
        res1 = eng.transcribe(str(audio_path))
        assert res1 == "testing fourier two b"
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["headers"] == {"Authorization": "Bearer test-placeholder-token"}
        assert kwargs["data"] == {
            "model": "oruk-fourier-2b",
            "language": "en",
            "response_format": "json",
        }
        assert (tmp_path / "clip.oruk_api").read_text() == "testing fourier two b"

        # Second call uses cache
        res2 = eng.transcribe(str(audio_path))
        assert res2 == "testing fourier two b"
        assert mock_post.call_count == 1

    # Malformed payload without 'text' raises ValueError and does not write cache
    bad_path = _write_flac(tmp_path / "bad.flac", sr=16000, seconds=0.5)
    bad_resp = mock.Mock()
    bad_resp.raise_for_status.return_value = None
    bad_resp.json.return_value = {"error": "bad payload"}
    with mock.patch.object(eng._session, "post", return_value=bad_resp):
        with pytest.raises(ValueError, match="missing 'text'"):
            eng.transcribe(str(bad_path))
    assert not (tmp_path / "bad.oruk_api").exists()

    eng.delete()


def test_benchmark_and_memory_cli_require_api_key_or_env(tmp_path: Path, monkeypatch):
    import benchmark
    import benchmark_memory_usage

    audio_path = _write_flac(tmp_path / "mem.flac", sr=16000, seconds=0.5)
    monkeypatch.delenv("ORUK_API_KEY", raising=False)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "benchmark.py",
            "--engine",
            "ORUK_FOURIER_2B_API",
            "--dataset",
            "LIBRI_SPEECH_TEST_CLEAN",
            "--dataset-folder",
            str(tmp_path),
            "--language",
            "EN",
        ],
    )
    with pytest.raises(ValueError, match="ORUK_API_KEY"):
        benchmark.main()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "benchmark_memory_usage.py",
            "--engine",
            "ORUK_FOURIER_2B_API",
            "--audio-path",
            str(audio_path),
            "--language",
            "EN",
        ],
    )
    with pytest.raises(ValueError, match="ORUK_API_KEY"):
        benchmark_memory_usage.main()
