from dataset import Datasets
from engine import Engines

WER = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 8.69,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 2.56,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 5.56,
        Datasets.TED_LIUM: 3.82,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 8.89,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 2.81,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.16,
        Datasets.TED_LIUM: 4.56,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 31.90,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 10.80,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 24.49,
        Datasets.TED_LIUM: 14.40,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: {
        Datasets.COMMON_VOICE: 18.17,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.15,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 13.02,
        Datasets.TED_LIUM: 6.14,
    },
    Engines.IBM_WATSON_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 39.38,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 10.87,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 26.16,
        Datasets.TED_LIUM: 11.71,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 17.47,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.59,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.13,
        Datasets.TED_LIUM: 7.73,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 16.23,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.32,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 11.33,
        Datasets.TED_LIUM: 7.18,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 24.42,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.88,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 13.76,
        Datasets.TED_LIUM: 6.55,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 17.93,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 4.26,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 10.36,
        Datasets.TED_LIUM: 5.44,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 12.70,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.31,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 7.20,
        Datasets.TED_LIUM: 4.75,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 10.16,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.27,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.21,
        Datasets.TED_LIUM: 4.58,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 8.98,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.67,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 5.36,
        Datasets.TED_LIUM: 4.60,
    },
}

RTF = {
    Engines.PICOVOICE_LEOPARD: {
        Datasets.TED_LIUM: 0.05,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.TED_LIUM: 0.09,
    },
    Engines.WHISPER_TINY: {
        Datasets.TED_LIUM: 0.15,
    },
    Engines.WHISPER_BASE: {
        Datasets.TED_LIUM: 0.28,
    },
    Engines.WHISPER_SMALL: {
        Datasets.TED_LIUM: 0.89,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.TED_LIUM: 1.50,
    },
}
