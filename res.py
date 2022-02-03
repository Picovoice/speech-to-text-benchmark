import matplotlib.pyplot as plt
import numpy as np

from dataset import Datasets
from engine import Engines

WER = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 15.94,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.20,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 9.58,
        Datasets.TED_LIUM: 4.25
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 12.09,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 4.96,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 9.66,
        Datasets.TED_LIUM: 4.99
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 30.68,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.23,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 24.94,
        Datasets.TED_LIUM: 15.00
    },
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: {
        Datasets.COMMON_VOICE: 18.39,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.62,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 13.59,
        Datasets.TED_LIUM: 6.68
    },
    Engines.IBM_WATSON_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 38.81,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.08,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 26.38,
        Datasets.TED_LIUM: 11.89
    },
    Engines.MOZILLA_DEEP_SPEECH: {
        Datasets.COMMON_VOICE: 43.82,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 7.27,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 21.45,
        Datasets.TED_LIUM: 18.90
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 23.10,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 7.08,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 16.28,
        Datasets.TED_LIUM: 10.89
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 17.13,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.39,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.45,
        Datasets.TED_LIUM: 9.04
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
    Engines.MOZILLA_DEEP_SPEECH: 'Mozilla\nDeepSpeech',
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
