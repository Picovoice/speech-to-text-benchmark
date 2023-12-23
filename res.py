import matplotlib.pyplot as plt
import numpy as np

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
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 0.25,
    },
    Engines.WHISPER_BASE: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 0.50,
    },
    Engines.WHISPER_SMALL: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 1.57,
    },
    Engines.WHISPER_MEDIUM: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 4.80,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 0.13,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 0.076,
    },
}

MEMORY = {
    Engines.WHISPER_TINY: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 913,
    },
    Engines.WHISPER_BASE: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 933,
    },
    Engines.WHISPER_SMALL: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 1696,
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 550,
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 561,
    },
}

ENGINE_WER = sorted([(e, sum(w for w in WER[e].values()) / len(Datasets)) for e in Engines], key=lambda x: x[1])

print('\n'.join(f"{e.value}: {x:.2f}" for e, x in sorted(ENGINE_WER, key=lambda x: x[1])))

GREY = (100 / 255, 100 / 255, 100 / 255)
BLUE = (55 / 255, 125 / 255, 255 / 255)

fig, ax = plt.subplots()

for i, (engine, wer) in enumerate(ENGINE_WER, start=1):
    color = BLUE if engine is Engines.PICOVOICE_LEOPARD or engine is Engines.PICOVOICE_CHEETAH else GREY
    ax.bar([i], [wer], 0.4, color=color)
    ax.text(i - 0.3, wer + 1, f'{wer:.2f}%', color=color)

ENGINE_TICKS = {
    Engines.AMAZON_TRANSCRIBE: 'Amazon',
    Engines.AZURE_SPEECH_TO_TEXT: 'Azure',
    Engines.GOOGLE_SPEECH_TO_TEXT: 'Google',
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: 'Google\nEnhanced',
    Engines.IBM_WATSON_SPEECH_TO_TEXT: 'IBM',
    Engines.WHISPER_TINY: 'Whisper\nTiny',
    Engines.WHISPER_BASE: 'Whisper\nBase',
    Engines.WHISPER_SMALL: 'Whisper\nSmall',
    Engines.WHISPER_MEDIUM: 'Whisper\nMedium',
    Engines.WHISPER_LARGE: 'Whisper\nLarge\n(Multilingual)',
    Engines.PICOVOICE_CHEETAH: 'Picovoice\nCheetah',
    Engines.PICOVOICE_LEOPARD: 'Picovoice\nLeopard'
}

for spine in plt.gca().spines.values():
    if spine.spine_type != 'bottom' and spine.spine_type != 'left':
        spine.set_visible(False)

plt.xticks(np.arange(1, len(Engines) + 1), [ENGINE_TICKS[x[0]] for x in ENGINE_WER], fontsize=9)

plt.yticks(np.arange(5, 30, 5), ["%s%%" % str(x) for x in np.arange(5, 30, 5)])

plt.ylabel('Word Error Rate (lower is better)')

plt.show()
