import matplotlib.pyplot as plt
import numpy as np

from dataset import Datasets
from engine import Engines

WER = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 15.94,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.20,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 9.58,
        Datasets.TEDLIUM: 4.25
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 12.09,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 4.96,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 9.66,
        Datasets.TEDLIUM: 4.99
    },
    Engines.GOOGLE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 30.68,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.23,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 24.94,
        Datasets.TEDLIUM: 15.00
    },
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: {
        Datasets.COMMON_VOICE: 18.39,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.62,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 13.59,
        Datasets.TEDLIUM: 6.68
    },
    Engines.IBM_WATSON_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 38.81,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.08,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 26.38,
        Datasets.TEDLIUM: 11.89
    },
    Engines.MOZILLA_DEEP_SPEECH: {
        Datasets.COMMON_VOICE: 43.82,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 7.27,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 21.45,
        Datasets.TEDLIUM: 18.90
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 18.93,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.73,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.84,
        Datasets.TEDLIUM: 9.83
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 18.93,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.73,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.84,
        Datasets.TEDLIUM: 9.83
    },
}

BLUE = (55 / 255, 125 / 255, 255 / 255)

fig, ax = plt.subplots()

print([sum(w for w in WER[e].values()) / len(Datasets) for e in Engines])

ax.bar(
    np.arange(1, len(Engines) + 1), [sum(w for w in WER[e].values()) / len(Datasets) for e in Engines],
    0.4,
    color=BLUE
)

ENGINE_TICKS = {
    Engines.AMAZON_TRANSCRIBE: 'Amazon',
    Engines.AZURE_SPEECH_TO_TEXT: 'Azure',
    Engines.GOOGLE_SPEECH_TO_TEXT: 'Google',
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: 'Google Enhanced',
    Engines.IBM_WATSON_SPEECH_TO_TEXT: 'IBM Watson',
    Engines.MOZILLA_DEEP_SPEECH: 'Mozilla DeepSpeech',
    Engines.PICOVOICE_CHEETAH: 'Picovoice Cheetah',
    Engines.PICOVOICE_LEOPARD: 'Picovoice Leopard'
}

for spine in plt.gca().spines.values():
    if spine.spine_type != 'bottom' and spine.spine_type != 'left':
        spine.set_visible(False)

plt.xticks(np.arange(1, len(Engines) + 1), [ENGINE_TICKS[e] for e in Engines], fontsize=9)

plt.yticks(np.arange(5, 40, 5), ["%s%%" % str(x) for x in np.arange(5, 40, 5)])

plt.ylabel('Word Error Rate', fontsize=9)
plt.title('Comparison of Word Error Rate of Speech-to-Text Engines\n')
plt.show()
