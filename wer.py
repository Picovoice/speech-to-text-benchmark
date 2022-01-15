import matplotlib.pyplot as plt
import numpy as np

# Amazon Transcribe | 5.20% | 9.58% | 4.25% | 15.94% | |
# Azure Speech-to-Text | 4.96% | 9.66% | 4.99% | 12.09% | |
# Google Speech-to-Text | 11.23% | 24.94% | 15.00% | 30.68% | |
# Google Speech-to-Text (Enhanced) | 6.62% | 13.59% | 6.68% | 18.39% | |
# IBM Watson Speech-to-Text | 11.08% | 26.38% | 11.89% | 38.81% | |
# Mozilla DeepSpeech | 7.27% | 21.45% | 18.90% | 43.82% | |
# Picovoice Cheetah | --- | --- | --- | --- | |
# Picovoice Leopard | 5.73% | 12.84% | 9.83% | 18.93% | |


BLUE = (55 / 255, 125 / 255, 255 / 255)

fig, ax = plt.subplots()

ax.bar(np.arange(1, 7), [6.58, 7.55, 8.21, 8.25, 11.58, 31.82], 0.4, color=BLUE)

for spine in plt.gca().spines.values():
    if spine.spine_type != 'bottom' and spine.spine_type != 'left':
        spine.set_visible(False)

plt.xticks(
    np.arange(1, 7),
    ['Picovoice\nLeopard', 'Mozilla\nDeepSpeech', 'Amazon\nTranscribe', 'Picovoice\nCheetah', 'Google\nSpeech-to-Text', 'CMU\nPocketSphinx'],
    fontsize=9)

plt.yticks(np.arange(5, 40, 5), ["%s%%" % str(x) for x in np.arange(5, 40, 5)])

plt.ylabel('Word Error Rate', fontsize=9)
plt.title('Comparison of Word Error Rate of Speech-to-Text Engines\n')
plt.show()
