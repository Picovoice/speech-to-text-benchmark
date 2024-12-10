import argparse
import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np

from benchmark import RESULTS_FOLDER
from dataset import Datasets
from engine import Engines
from results import *

Color = Tuple[float, float, float]


def rgb_from_hex(x: str) -> Color:
    x = x.strip("# ")
    assert len(x) == 6
    return int(x[:2], 16) / 255, int(x[2:4], 16) / 255, int(x[4:], 16) / 255


BLACK = rgb_from_hex("#000000")
GREY1 = rgb_from_hex("#4F4F4F")
GREY2 = rgb_from_hex("#5F5F5F")
GREY3 = rgb_from_hex("#6F6F6F")
GREY4 = rgb_from_hex("#7F7F7F")
GREY5 = rgb_from_hex("#8F8F8F")
WHITE = rgb_from_hex("#FFFFFF")
BLUE = rgb_from_hex("#377DFF")

ENGINE_PRINT_NAMES = {
    Engines.AMAZON_TRANSCRIBE: "Amazon",
    Engines.AZURE_SPEECH_TO_TEXT: "Azure",
    Engines.GOOGLE_SPEECH_TO_TEXT: "Google",
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: "Google\nEnhanced",
    Engines.IBM_WATSON_SPEECH_TO_TEXT: "IBM",
    Engines.WHISPER_TINY: "Whisper\nTiny",
    Engines.WHISPER_BASE: "Whisper\nBase",
    Engines.WHISPER_SMALL: "Whisper\nSmall",
    Engines.WHISPER_MEDIUM: "Whisper\nMedium",
    Engines.WHISPER_LARGE: "Whisper\nLarge",
    Engines.PICOVOICE_CHEETAH: "Picovoice\nCheetah",
    Engines.PICOVOICE_LEOPARD: "Picovoice\nLeopard",
}

ENGINE_COLORS = {
    Engines.AMAZON_TRANSCRIBE: GREY5,
    Engines.AZURE_SPEECH_TO_TEXT: GREY4,
    Engines.GOOGLE_SPEECH_TO_TEXT: GREY3,
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: GREY3,
    Engines.IBM_WATSON_SPEECH_TO_TEXT: GREY2,
    Engines.WHISPER_LARGE: GREY1,
    Engines.WHISPER_MEDIUM: GREY1,
    Engines.WHISPER_SMALL: GREY1,
    Engines.WHISPER_BASE: GREY1,
    Engines.WHISPER_TINY: GREY1,
    Engines.PICOVOICE_LEOPARD: BLUE,
    Engines.PICOVOICE_CHEETAH: BLUE,
}


def _plot_wer(
    engine_wer: Dict[Engines, Dict[Datasets, float]], save_path: str, show: bool = False
) -> None:
    sorted_wer = sorted(
        [
            (
                e,
                round(
                    sum(w for w in engine_wer[e].values()) / len(engine_wer[e]) + 1e-9,
                    1,
                ),
            )
            for e in engine_wer.keys()
        ],
        key=lambda x: x[1],
    )
    print("\n".join(f"{e.value}: {x}" for e, x in sorted_wer))

    _, ax = plt.subplots(figsize=(12, 6))

    for i, (engine, wer) in enumerate(sorted_wer, start=1):
        color = ENGINE_COLORS[engine]
        ax.bar([i], [wer], 0.4, color=color)
        ax.text(
            i,
            wer + 0.5,
            f"{wer}%",
            color=color,
            ha="center",
            va="bottom",
        )

    for spine in plt.gca().spines.values():
        if spine.spine_type != "bottom" and spine.spine_type != "left":
            spine.set_visible(False)

    plt.xticks(
        np.arange(1, len(engine_wer) + 1),
        [ENGINE_PRINT_NAMES[x[0]] for x in sorted_wer],
        fontsize=9,
    )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    plt.ylabel("Word Error Rate (lower is better)")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    print(f"Saved plot to `{save_path}`")

    if show:
        plt.show()

    plt.close()


def _plot_cpu(
    save_folder: str, show: bool, dataset: Datasets = Datasets.TED_LIUM
) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    x_limit = 0
    for engine_type, engine_value in RTF.items():
        core_hour = engine_value[dataset] * 100
        core_hour = round(core_hour, 0)
        x_limit = max(x_limit, core_hour)
        ax.barh(
            ENGINE_PRINT_NAMES[engine_type],
            core_hour,
            height=0.5,
            color=ENGINE_COLORS[engine_type],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine_type],
        )
        ax.text(
            core_hour + 30,
            ENGINE_PRINT_NAMES[engine_type],
            f"{core_hour:.0f}\nCore-hour",
            ha="center",
            va="center",
            fontsize=12,
            color=ENGINE_COLORS[engine_type],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xlim([0, x_limit + 50])
    ax.set_xticks([])
    ax.set_ylim([-0.5, 5.5])
    plt.title(
        "Core-hour required to process 100 hours of audio (lower is better)",
        fontsize=12,
    )
    plot_path = os.path.join(save_folder, "cpu_usage_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    save_folder = os.path.join(RESULTS_FOLDER, "plots")

    _plot_wer(WER, save_path=os.path.join(save_folder, "WER.png"), show=args.show)
    _plot_wer(WER_FR, save_path=os.path.join(save_folder, "WER_FR.png"), show=args.show)
    _plot_wer(WER_DE, save_path=os.path.join(save_folder, "WER_DE.png"), show=args.show)
    _plot_wer(WER_ES, save_path=os.path.join(save_folder, "WER_ES.png"), show=args.show)
    _plot_wer(WER_IT, save_path=os.path.join(save_folder, "WER_IT.png"), show=args.show)
    _plot_wer(WER_PT, save_path=os.path.join(save_folder, "WER_PT.png"), show=args.show)
    _plot_cpu(save_folder=save_folder, show=args.show, dataset=Datasets.TED_LIUM)


if __name__ == "__main__":
    main()
