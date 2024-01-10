from dataset import Datasets
from engine import Engines

WER = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 8.76,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 2.68,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 5.69,
        Datasets.TED_LIUM: 3.92,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 9.04,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.03,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.40,
        Datasets.TED_LIUM: 4.65
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 31.96,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 10.96,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 24.68,
        Datasets.TED_LIUM: 14.51
    },
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: {
        Datasets.COMMON_VOICE: 18.25,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.34,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 13.27,
        Datasets.TED_LIUM: 6.24
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 24.52,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.15,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 14.05,
        Datasets.TED_LIUM: 6.65
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 18.04,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 4.54,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 10.66,
        Datasets.TED_LIUM: 5.52,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 12.81,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.58,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 7.51,
        Datasets.TED_LIUM: 4.84,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 10.28,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.52,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.51,
        Datasets.TED_LIUM: 4.68,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 12.14,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 3.89,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 5.68,
        Datasets.TED_LIUM: 4.69,
    },
    Engines.IBM_WATSON_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 39.46,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.06,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 26.35,
        Datasets.TED_LIUM: 11.80
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 17.53,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.87,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.46,
        Datasets.TED_LIUM: 7.83,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 16.28,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.56,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 11.61,
        Datasets.TED_LIUM: 7.28,
    },
}

RTF = {
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
    Engines.PICOVOICE_CHEETAH: {
        Datasets.TED_LIUM: 0.09,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.TED_LIUM: 0.05,
    },
}

MEMORY = {
    Engines.WHISPER_TINY: {
        Datasets.TED_LIUM: 6_200 / 10,
    },
    Engines.WHISPER_BASE: {
        Datasets.TED_LIUM: 8_000 / 10,
    },
    Engines.WHISPER_SMALL: {
        Datasets.TED_LIUM: 15_000 / 10,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.TED_LIUM: 40_000 / 10,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.TED_LIUM: 3_000 / 10,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.TED_LIUM: 8_000 / 10,
    },
}
