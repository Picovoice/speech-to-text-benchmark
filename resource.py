import matplotlib.pyplot as plt

fig, ax = plt.subplots()

RED = (222 / 255, 68 / 255, 55 / 255)
ORANGE = (255 / 255, 193 / 255, 7 / 255)
BLUE = (55 / 255, 125 / 255, 255 / 255)
GREEN = (40 / 255, 167 / 255, 69 / 255)

ax.bar([0.7, 2.7, 4.7], [2 / 46, 45.0 / 1146.8, 6.6 / 31.82], 0.2, label='Picovoice\nLeopard\n', color=GREEN)
ax.bar([0.9, 2.9, 4.9], [4 / 46, 45.0 / 1146.8, 8.3 / 31.82], 0.2, label='Picovoice\nCheetah\n', color=BLUE)
ax.bar([1.1, 3.1, 5.1], [32 / 46, 97.8 / 1146.8, 31.82 / 31.82], 0.2, label='CMU\nPocketSphinx\n', color=ORANGE)
ax.bar([1.3, 3.3, 5.3], [46 / 46, 1146.8 / 1146.8, 7.6 / 31.82], 0.2, label='Mozilla\nDeepSpeech\n', color=RED)

for spine in plt.gca().spines.values():
    if spine.spine_type != 'bottom':
        spine.set_visible(False)

plt.xticks([1, 3, 5], ['Relative\nCPU Usage', 'Relative\nModel Size', 'Relative\nWord Error Rate'])
plt.yticks([], [])

plt.xlim(0, 8)

plt.legend(frameon=False, loc='upper right', prop=dict(size=10))
plt.title('Comparison of Offline Speech-to-Text Engines\n')
plt.show()
