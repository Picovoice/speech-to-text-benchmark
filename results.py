from dataset import Datasets
from engine import Engines

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

WER_EN = {
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
        Datasets.COMMON_VOICE: 18.2,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.3,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 11.9,
        Datasets.TED_LIUM: 7,
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
        Datasets.COMMON_VOICE: 14.8,
        Datasets.MLS: 14.2,
        Datasets.VOX_POPULI: 15.1,
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
        Datasets.COMMON_VOICE: 7.8,
        Datasets.MLS: 8.2,
        Datasets.VOX_POPULI: 12.9,
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
        Datasets.COMMON_VOICE: 9.3,
        Datasets.MLS: 11.0,
        Datasets.VOX_POPULI: 16.9,
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
        Datasets.COMMON_VOICE: 8.9,
        Datasets.MLS: 17.7,
        Datasets.VOX_POPULI: 19.9,
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
        Datasets.COMMON_VOICE: 10.5,
        Datasets.MLS: 15.9,
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

PER_EN = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.VOX_POPULI: 19.1,
        Datasets.FLEURS: 12.1,
        Datasets.COMMON_VOICE: 3.8,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 23.0,
        Datasets.FLEURS: 18.9,
        Datasets.COMMON_VOICE: 6.0,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 45.7,
        Datasets.FLEURS: 43.4,
        Datasets.COMMON_VOICE: 21.3,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.VOX_POPULI: 30.0,
        Datasets.FLEURS: 18.3,
        Datasets.COMMON_VOICE: 6.0,
    },
    Engines.WHISPER_TINY: {
        Datasets.VOX_POPULI: 24.7,
        Datasets.FLEURS: 15.4,
        Datasets.COMMON_VOICE: 12.2,
    },
    Engines.WHISPER_BASE: {
        Datasets.VOX_POPULI: 23.7,
        Datasets.FLEURS: 14.2,
        Datasets.COMMON_VOICE: 9.7,
    },
    Engines.WHISPER_SMALL: {
        Datasets.VOX_POPULI: 22.5,
        Datasets.FLEURS: 12.2,
        Datasets.COMMON_VOICE: 10.8,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.VOX_POPULI: 21.7,
        Datasets.FLEURS: 10.2,
        Datasets.COMMON_VOICE: 10.4,
    },
    Engines.WHISPER_LARGE: {
        Datasets.VOX_POPULI: 21.4,
        Datasets.FLEURS: 11.6,
        Datasets.COMMON_VOICE: 10.2,
    },
}

PER_FR = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.VOX_POPULI: 33.1,
        Datasets.FLEURS: 11.8,
        Datasets.COMMON_VOICE: 11.2,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 25.8,
        Datasets.FLEURS: 12.5,
        Datasets.COMMON_VOICE: 6.2,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 30.7,
        Datasets.FLEURS: 24.5,
        Datasets.COMMON_VOICE: 26.6,
    },
    Engines.WHISPER_LARGE: {
        Datasets.VOX_POPULI: 23.8,
        Datasets.FLEURS: 9.4,
        Datasets.COMMON_VOICE: 10.8,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.VOX_POPULI: 22.8,
        Datasets.FLEURS: 11.1,
        Datasets.COMMON_VOICE: 8.7,
    },
    Engines.WHISPER_SMALL: {
        Datasets.VOX_POPULI: 25,
        Datasets.FLEURS: 13.4,
        Datasets.COMMON_VOICE: 10.2,
    },
    Engines.WHISPER_BASE: {
        Datasets.VOX_POPULI: 26.8,
        Datasets.FLEURS: 18.5,
        Datasets.COMMON_VOICE: 10.9,
    },
    Engines.WHISPER_TINY: {
        Datasets.VOX_POPULI: 31.5,
        Datasets.FLEURS: 27.3,
        Datasets.COMMON_VOICE: 15,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.VOX_POPULI: 38.3,
        Datasets.FLEURS: 23.7,
        Datasets.COMMON_VOICE: 8.8,
    },
}

PER_ES = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.VOX_POPULI: 32.7,
        Datasets.FLEURS: 15.2,
        Datasets.COMMON_VOICE: 5.6,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 26.9,
        Datasets.FLEURS: 13.6,
        Datasets.COMMON_VOICE: 3.9,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 42.3,
        Datasets.FLEURS: 45,
        Datasets.COMMON_VOICE: 58.7,
    },
    Engines.WHISPER_LARGE: {
        Datasets.VOX_POPULI: 26.4,
        Datasets.FLEURS: 9.2,
        Datasets.COMMON_VOICE: 6.1,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.VOX_POPULI: 26.7,
        Datasets.FLEURS: 15.1,
        Datasets.COMMON_VOICE: 14.4,
    },
    Engines.WHISPER_SMALL: {
        Datasets.VOX_POPULI: 29.8,
        Datasets.FLEURS: 12.1,
        Datasets.COMMON_VOICE: 10.9,
    },
    Engines.WHISPER_BASE: {
        Datasets.VOX_POPULI: 32.2,
        Datasets.FLEURS: 15,
        Datasets.COMMON_VOICE: 16.9,
    },
    Engines.WHISPER_TINY: {
        Datasets.VOX_POPULI: 33.3,
        Datasets.FLEURS: 17.6,
        Datasets.COMMON_VOICE: 18.9,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.VOX_POPULI: 47.8,
        Datasets.FLEURS: 21,
        Datasets.COMMON_VOICE: 5.7,
    },
}

PER_DE = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.VOX_POPULI: 24.3,
        Datasets.FLEURS: 14.5,
        Datasets.COMMON_VOICE: 3.1,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 30.2,
        Datasets.FLEURS: 19.4,
        Datasets.COMMON_VOICE: 8.3,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 29.4,
        Datasets.FLEURS: 26.9,
        Datasets.COMMON_VOICE: 15.9,
    },
    Engines.WHISPER_LARGE: {
        Datasets.VOX_POPULI: 20.5,
        Datasets.FLEURS: 15.3,
        Datasets.COMMON_VOICE: 6.5,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.VOX_POPULI: 21.3,
        Datasets.FLEURS: 10.2,
        Datasets.COMMON_VOICE: 3.4,
    },
    Engines.WHISPER_SMALL: {
        Datasets.VOX_POPULI: 22.6,
        Datasets.FLEURS: 11.5,
        Datasets.COMMON_VOICE: 3.7,
    },
    Engines.WHISPER_BASE: {
        Datasets.VOX_POPULI: 25.6,
        Datasets.FLEURS: 14.9,
        Datasets.COMMON_VOICE: 5.8,
    },
    Engines.WHISPER_TINY: {
        Datasets.VOX_POPULI: 30,
        Datasets.FLEURS: 22,
        Datasets.COMMON_VOICE: 9.3,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.VOX_POPULI: 29.7,
        Datasets.FLEURS: 24.3,
        Datasets.COMMON_VOICE: 3.2,
    },
}

PER_IT = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.VOX_POPULI: 46.4,
        Datasets.FLEURS: 63.4,
        Datasets.COMMON_VOICE: 6.5,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 26.9,
        Datasets.FLEURS: 16.3,
        Datasets.COMMON_VOICE: 3.5,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.VOX_POPULI: 46.9,
        Datasets.FLEURS: 25.5,
        Datasets.COMMON_VOICE: 27.9,
    },
    Engines.WHISPER_LARGE: {
        Datasets.VOX_POPULI: 36.4,
        Datasets.FLEURS: 12.2,
        Datasets.COMMON_VOICE: 11.9,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.VOX_POPULI: 39.5,
        Datasets.FLEURS: 12.5,
        Datasets.COMMON_VOICE: 15,
    },
    Engines.WHISPER_SMALL: {
        Datasets.VOX_POPULI: 39,
        Datasets.FLEURS: 12.9,
        Datasets.COMMON_VOICE: 10.8,
    },
    Engines.WHISPER_BASE: {
        Datasets.VOX_POPULI: 45.7,
        Datasets.FLEURS: 18.2,
        Datasets.COMMON_VOICE: 19.8,
    },
    Engines.WHISPER_TINY: {
        Datasets.VOX_POPULI: 45.3,
        Datasets.FLEURS: 26.3,
        Datasets.COMMON_VOICE: 27.4,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.VOX_POPULI: 48.6,
        Datasets.FLEURS: 27.2,
        Datasets.COMMON_VOICE: 5.6,
    },
}

PER_PT = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.FLEURS: 23.2,
        Datasets.COMMON_VOICE: 15.8,
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.FLEURS: 19.4,
        Datasets.COMMON_VOICE: 11.9,
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.FLEURS: 32.1,
        Datasets.COMMON_VOICE: 31.3,
    },
    Engines.WHISPER_LARGE: {
        Datasets.FLEURS: 16.6,
        Datasets.COMMON_VOICE: 9.2,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.FLEURS: 12.8,
        Datasets.COMMON_VOICE: 11.8,
    },
    Engines.WHISPER_SMALL: {
        Datasets.FLEURS: 13.9,
        Datasets.COMMON_VOICE: 11.6,
    },
    Engines.WHISPER_BASE: {
        Datasets.FLEURS: 16.9,
        Datasets.COMMON_VOICE: 15.4,
    },
    Engines.WHISPER_TINY: {
        Datasets.FLEURS: 22.7,
        Datasets.COMMON_VOICE: 22.2,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.FLEURS: 32.8,
        Datasets.COMMON_VOICE: 12.4,
    },
}


__all__ = [
    "RTF",
    "WER_EN",
    "WER_DE",
    "WER_ES",
    "WER_FR",
    "WER_IT",
    "WER_PT",
    "PER_EN",
    "PER_DE",
    "PER_ES",
    "PER_FR",
    "PER_IT",
    "PER_PT",
]
