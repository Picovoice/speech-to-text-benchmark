import matplotlib.pyplot as plt
import numpy as np

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
