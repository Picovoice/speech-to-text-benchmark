import matplotlib.pyplot as plt
import numpy as np

from dataset import Datasets
from engine import Engines

WER = {
    Engines.AMAZON_TRANSCRIBE: {
        Datasets.COMMON_VOICE: 8.76,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 2.68,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 5.69,
        Datasets.TED_LIUM: 4.25  # TODO
    },
    Engines.AZURE_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 9.85,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 7.15,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 11.26,
        Datasets.TED_LIUM: 9.75
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
        Datasets.COMMON_VOICE: 18.39,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 6.62,  # TODO
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.55,  # TODO
        Datasets.TED_LIUM: 6.68  # TODO
    },
    Engines.IBM_WATSON_SPEECH_TO_TEXT: {
        Datasets.COMMON_VOICE: 38.81,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 11.06,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 26.38,  # TODO
        Datasets.TED_LIUM: 11.89  # TODO
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 23.10,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.87,
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.46,
        Datasets.TED_LIUM: 7.83,  #  7.79 # WITHOUT new normalizations
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 16.68,
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.39,  # TODO
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.45,  # TODO
        Datasets.TED_LIUM: 9.04  # TODO
    },
}

RTF = {
    Engines.WHISPER_TINY: {
        Datasets.COMMON_VOICE: 23.10,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.87,   # TODO
        Datasets.LIBRI_SPEECH_TEST_OTHER: 6.55,  # TODO
        Datasets.TED_LIUM: 7.83,  # TODO
    },
    Engines.PICOVOICE_CHEETAH: {
        Datasets.COMMON_VOICE: 23.10,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.87,   # TODO
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.46,  # TODO
        Datasets.TED_LIUM: 7.83,  # TODO
    },
    Engines.PICOVOICE_LEOPARD: {
        Datasets.COMMON_VOICE: 16.68,  # TODO
        Datasets.LIBRI_SPEECH_TEST_CLEAN: 5.39,  # TODO
        Datasets.LIBRI_SPEECH_TEST_OTHER: 12.45,  # TODO
        Datasets.TED_LIUM: 9.04  # TODO
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
