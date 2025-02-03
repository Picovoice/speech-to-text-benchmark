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
        Datasets.COMMON_VOICE: 17.3,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.4,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.0,
        Datasets.TED_LIUM: 6.8,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 16.1,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.1,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 11.1,
        Datasets.TED_LIUM: 6.4,
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


WER_FR = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 6.0,
        Datasets.MLS: 4.4,
        Datasets.VOX_POPULI: 8.6,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 11.1,
        Datasets.MLS: 9.0,
        Datasets.VOX_POPULI: 11.8,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 14.3,
        Datasets.MLS: 14.2,
        Datasets.VOX_POPULI: 15.1,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 14.5,
        Datasets.MLS: 14.5,
        Datasets.VOX_POPULI: 14.9,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 15.9,
        Datasets.MLS: 19.2,
        Datasets.VOX_POPULI: 17.5,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 49.8,
        Datasets.MLS: 36.2,
        Datasets.VOX_POPULI: 32.1,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 35.4,
        Datasets.MLS: 24.4,
        Datasets.VOX_POPULI: 23.3,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 19.2,
        Datasets.MLS: 13.5,
        Datasets.VOX_POPULI: 15.3,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 13.1,
        Datasets.MLS: 8.6,
        Datasets.VOX_POPULI: 12.1,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 9.3,
        Datasets.MLS: 4.6,
        Datasets.VOX_POPULI: 10.9,
    },
}

WER_ES = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 3.9,
        Datasets.MLS: 3.3,
        Datasets.VOX_POPULI: 8.7,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 6.3,
        Datasets.MLS: 5.8,
        Datasets.VOX_POPULI: 9.4,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 6.6,
        Datasets.MLS: 9.2,
        Datasets.VOX_POPULI: 11.6,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 8.3,
        Datasets.MLS: 8.0,
        Datasets.VOX_POPULI: 11.4,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 7.6,
        Datasets.MLS: 14.9,
        Datasets.VOX_POPULI: 14.1,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 33.3,
        Datasets.MLS: 20.6,
        Datasets.VOX_POPULI: 22.7,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 20.2,
        Datasets.MLS: 13.0,
        Datasets.VOX_POPULI: 15.3,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 9.8,
        Datasets.MLS: 7.7,
        Datasets.VOX_POPULI: 11.4,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 6.2,
        Datasets.MLS: 4.8,
        Datasets.VOX_POPULI: 9.7,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 4.0,
        Datasets.MLS: 2.9,
        Datasets.VOX_POPULI: 9.7,
    },
}

WER_DE = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 5.3,
        Datasets.MLS: 2.9,
        Datasets.VOX_POPULI: 14.6,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 6.9,
        Datasets.MLS: 5.4,
        Datasets.VOX_POPULI: 13.1,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 9.2,
        Datasets.MLS: 13.9,
        Datasets.VOX_POPULI: 17.2,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 8.4,
        Datasets.MLS: 12.1,
        Datasets.VOX_POPULI: 17.0,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 8.2,
        Datasets.MLS: 11.6,
        Datasets.VOX_POPULI: 23.6,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 39.5,
        Datasets.MLS: 28.6,
        Datasets.VOX_POPULI: 33.0,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 26.9,
        Datasets.MLS: 19.8,
        Datasets.VOX_POPULI: 24.0,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 13.8,
        Datasets.MLS: 11.2,
        Datasets.VOX_POPULI: 16.2,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 8.3,
        Datasets.MLS: 7.6,
        Datasets.VOX_POPULI: 13.5,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 5.3,
        Datasets.MLS: 4.4,
        Datasets.VOX_POPULI: 12.5,
    },
}

WER_IT = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 4.1,
        Datasets.MLS: 9.1,
        Datasets.VOX_POPULI: 16.1,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 5.8,
        Datasets.MLS: 14.0,
        Datasets.VOX_POPULI: 17.8,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 5.5,
        Datasets.MLS: 19.6,
        Datasets.VOX_POPULI: 18.7,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 8.6,
        Datasets.MLS: 17.6,
        Datasets.VOX_POPULI: 20.1,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 13.0,
        Datasets.MLS: 27.7,
        Datasets.VOX_POPULI: 22.2,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 48.1,
        Datasets.MLS: 43.3,
        Datasets.VOX_POPULI: 43.5,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 32.3,
        Datasets.MLS: 31.6,
        Datasets.VOX_POPULI: 31.6,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 15.4,
        Datasets.MLS: 20.6,
        Datasets.VOX_POPULI: 22.7,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 8.7,
        Datasets.MLS: 14.9,
        Datasets.VOX_POPULI: 19.3,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 4.9,
        Datasets.MLS: 8.8,
        Datasets.VOX_POPULI: 21.8,
    },
}

WER_PT = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 5.4,
        Datasets.MLS: 7.8,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 7.4,
        Datasets.MLS: 9.0,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 8.8,
        Datasets.MLS: 14.2,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 10.6,
        Datasets.MLS: 16.1,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 17.1,
        Datasets.MLS: 20.0,
    },
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 47.7,
        Datasets.MLS: 34.6,
    },
    Engines.WHISPER_BASE: {
        Datasets.COMMON_VOICE: 31.2,
        Datasets.MLS: 22.7,
    },
    Engines.WHISPER_SMALL: {
        Datasets.COMMON_VOICE: 15.6,
        Datasets.MLS: 13.0,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.COMMON_VOICE: 9.6,
        Datasets.MLS: 8.1,
    },
    Engines.WHISPER_LARGE: {
        Datasets.COMMON_VOICE: 5.9,
        Datasets.MLS: 5.4,
    },
}


__all__ = [
    "RTF",
    "WER",
    "WER_DE",
    "WER_ES",
    "WER_FR",
    "WER_IT",
    "WER_PT",
]
