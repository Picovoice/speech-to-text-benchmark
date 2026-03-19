import argparse
import os
from typing import (
    Dict,
    Tuple
)

import matplotlib.pyplot as plt
import numpy as np

from benchmark import RESULTS_FOLDER
from dataset import Datasets
from engine import (
    Engines,
    StreamingEngines
)
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
    Engines.AMAZON_TRANSCRIBE_STREAMING: "Amazon\nStreaming",
    Engines.AZURE_SPEECH_TO_TEXT: "Azure",
    Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME: "Azure\nReal-time",
    Engines.GOOGLE_SPEECH_TO_TEXT: "Google",
    Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING: "Google\nStreaming",
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: "Google\nEnhanced",
    Engines.IBM_WATSON_SPEECH_TO_TEXT: "IBM",
    Engines.WHISPER_TINY: "Whisper\nTiny",
    Engines.WHISPER_BASE: "Whisper\nBase",
    Engines.WHISPER_SMALL: "Whisper\nSmall",
    Engines.WHISPER_MEDIUM: "Whisper\nMedium",
    Engines.WHISPER_LARGE: "Whisper\nLarge",
    Engines.PICOVOICE_CHEETAH: "Picovoice\nCheetah",
    Engines.PICOVOICE_LEOPARD: "Picovoice\nLeopard",
    Engines.VOSK_STREAMING_SMALL: "Vosk\nSmall",
    Engines.VOSK_STREAMING_LARGE: "Vosk\nLarge",
    Engines.MOONSHINE_STREAMING_TINY: "Moonshine\nTiny",
    Engines.MOONSHINE_STREAMING_SMALL: "Moonshine\nSmall",
    Engines.MOONSHINE_STREAMING_MEDIUM: "Moonshine\nMedium",
    Engines.WHISPER_CPP_STREAMING_TINY: "Whisper.cpp\nTiny",
    Engines.WHISPER_CPP_STREAMING_BASE: "Whisper.cpp\nBase",
    Engines.WHISPER_CPP_STREAMING_SMALL: "Whisper.cpp\nSmall",
    Engines.WHISPER_CPP_STREAMING_MEDIUM: "Whisper.cpp\nMedium",
    Engines.WHISPER_CPP_STREAMING_LARGE_V3: "Whisper.cpp\nLarge-v3",
    Engines.WHISPER_CPP_STREAMING_LARGE_TURBO: "Whisper.cpp\nTurbo",
}

ENGINE_COLORS = {
    Engines.AMAZON_TRANSCRIBE: GREY5,
    Engines.AMAZON_TRANSCRIBE_STREAMING: GREY5,
    Engines.AZURE_SPEECH_TO_TEXT: GREY4,
    Engines.AZURE_SPEECH_TO_TEXT_REAL_TIME: GREY4,
    Engines.GOOGLE_SPEECH_TO_TEXT: GREY3,
    Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING: GREY3,
    Engines.GOOGLE_SPEECH_TO_TEXT_ENHANCED: GREY3,
    Engines.IBM_WATSON_SPEECH_TO_TEXT: GREY2,
    Engines.WHISPER_LARGE: GREY1,
    Engines.WHISPER_MEDIUM: GREY1,
    Engines.WHISPER_SMALL: GREY1,
    Engines.WHISPER_BASE: GREY1,
    Engines.WHISPER_TINY: GREY1,
    Engines.PICOVOICE_LEOPARD: BLUE,
    Engines.PICOVOICE_CHEETAH: BLUE,
    Engines.VOSK_STREAMING_SMALL: GREY1,
    Engines.VOSK_STREAMING_LARGE: GREY1,
    Engines.MOONSHINE_STREAMING_TINY: GREY1,
    Engines.MOONSHINE_STREAMING_SMALL: GREY1,
    Engines.MOONSHINE_STREAMING_MEDIUM: GREY1,
    Engines.WHISPER_CPP_STREAMING_TINY: GREY1,
    Engines.WHISPER_CPP_STREAMING_BASE: GREY1,
    Engines.WHISPER_CPP_STREAMING_SMALL: GREY1,
    Engines.WHISPER_CPP_STREAMING_MEDIUM: GREY1,
    Engines.WHISPER_CPP_STREAMING_LARGE_V3: GREY1,
    Engines.WHISPER_CPP_STREAMING_LARGE_TURBO: GREY1,
}


def _plot_error_rate(
    engine_error_rate: Dict[Engines, Dict[Datasets, float]],
    save_path: str,
    streaming: bool,
    show: bool = False,
    punctuation: bool = False,
) -> None:
    sorted_error_rates = sorted(
        [
            (e, round(sum(w for w in engine_error_rate[e].values()) / len(engine_error_rate[e]) + 1e-9, 1))
            for e in engine_error_rate.keys()
        ],
        key=lambda x: x[1],
    )
    if streaming:
        sorted_error_rates = [(e, v) for e, v in sorted_error_rates if e in StreamingEngines]
    else:
        sorted_error_rates = [(e, v) for e, v in sorted_error_rates if e not in StreamingEngines]
    print("\n".join(f"{e.value}: {x}" for e, x in sorted_error_rates))

    _, ax = plt.subplots(figsize=(12, 6))

    for i, (engine, error_rate) in enumerate(sorted_error_rates, start=1):
        color = ENGINE_COLORS[engine]
        ax.bar([i], [error_rate], 0.4, color=color)
        ax.text(
            i,
            error_rate + 0.5,
            f"{error_rate}%",
            color=color,
            ha="center",
            va="bottom",
        )

    for spine in plt.gca().spines.values():
        if spine.spine_type != "bottom" and spine.spine_type != "left":
            spine.set_visible(False)

    plt.xticks(
        np.arange(1, len(sorted_error_rates) + 1),
        [ENGINE_PRINT_NAMES[x[0]] for x in sorted_error_rates],
        fontsize=8,
    )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    if punctuation:
        plt.ylabel("Punctuation Error Rate (lower is better)")
    else:
        plt.ylabel("Word Error Rate (lower is better)")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    print(f"Saved plot to `{save_path}`")

    if show:
        plt.show()

    plt.close()


def _plot_cpu(save_folder: str, show: bool, dataset: Datasets = Datasets.TED_LIUM) -> None:
    num_engines = len(RTF)
    fig_height = max(6, num_engines * 0.6 + 1)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    x_limit = 0
    for engine_type, engine_value in RTF.items():
        core_hour = engine_value[dataset] * 100
        core_hour = round(core_hour, 1)
        x_limit = max(x_limit, core_hour)
        ax.barh(
            ENGINE_PRINT_NAMES[engine_type],
            core_hour,
            height=0.5,
            color=ENGINE_COLORS[engine_type],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine_type],
        )

    text_offset = x_limit * 0.03
    for engine_type, engine_value in RTF.items():
        core_hour = round(engine_value[dataset] * 100, 1)
        ax.text(
            core_hour + text_offset,
            ENGINE_PRINT_NAMES[engine_type],
            f"{core_hour:.1f} Core-hour",
            ha="left",
            va="center",
            fontsize=11,
            color=ENGINE_COLORS[engine_type],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xlim([0, x_limit * 1.25])
    ax.set_xticks([])
    ax.set_ylim([-0.5, num_engines - 0.5])
    plt.subplots_adjust(left=0.15)
    plt.title(
        "Core-hour required to process 100 hours of audio (lower is better)",
        fontsize=12,
    )
    plot_path = os.path.join(save_folder, "cpu_usage_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    plt.close()


def _plot_latency(save_folder: str, show: bool, dataset: Datasets = Datasets.LIBRI_SPEECH_TEST_CLEAN) -> None:
    num_engines = len(LATENCIES)
    fig_height = max(6, num_engines * 0.6 + 1)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    x_limit = 0
    for engine_type, engine_value in LATENCIES.items():
        latency = int(engine_value[dataset])
        x_limit = max(x_limit, latency)
        ax.barh(
            ENGINE_PRINT_NAMES[engine_type],
            latency,
            height=0.5,
            color=ENGINE_COLORS[engine_type],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine_type],
        )

    text_offset = x_limit * 0.03
    for engine_type, engine_value in LATENCIES.items():
        latency = int(engine_value[dataset])
        ax.text(
            latency + text_offset,
            ENGINE_PRINT_NAMES[engine_type],
            f"{latency}ms",
            ha="left",
            va="center",
            fontsize=11,
            color=ENGINE_COLORS[engine_type],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xlim([0, x_limit * 1.25])
    ax.set_xticks([])
    ax.set_ylim([-0.5, num_engines - 0.5])
    plt.subplots_adjust(left=0.15)
    plt.title(
        "Average word emission latency (lower is better)",
        fontsize=12,
    )
    plot_path = os.path.join(save_folder, "latency_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    plt.close()


def _plot_error_rate_latency_grid(save_folder: str, show: bool):
    fig, ax = plt.subplots(figsize=(10, 8))

    engines = list(LATENCIES.keys())

    error_rates = []
    latencies = []
    colors = []
    for e in engines:
        error_rates.append(round(sum(w for w in WER_EN[e].values()) / len(WER_EN[e]) + 1e-9, 1))
        latencies.append(LATENCIES[e][Datasets.LIBRI_SPEECH_TEST_CLEAN])
        colors.append(ENGINE_COLORS[e])

    ax.scatter(error_rates, latencies, color=colors, s=150, alpha=0.8, edgecolors="black", linewidth=2)

    for i, engine in enumerate(engines):
        if engine in [
            Engines.MOONSHINE_STREAMING_SMALL,
            Engines.MOONSHINE_STREAMING_MEDIUM,
            Engines.GOOGLE_SPEECH_TO_TEXT_STREAMING,
        ]:
            y_offset = -20
        else:
            y_offset = 20

        ax.annotate(
            ENGINE_PRINT_NAMES[engine],
            (error_rates[i], latencies[i]),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=9,
            color=colors[i],
            weight="bold",
        )

    ax.set_xlabel("Word Error Rate", fontsize=12)
    ax.set_ylabel("Latency", fontsize=12)

    wer_min = min(error_rates) + 1
    wer_max = max(error_rates) - 1
    lat_min = min(latencies)
    lat_max = max(latencies) - 150
    wer_pad = max((wer_max - wer_min) * 0.15, 1)
    lat_pad = max((lat_max - lat_min) * 0.15, 50)
    ax.set_xlim(wer_min - wer_pad, wer_max + wer_pad)
    ax.set_ylim(lat_min - lat_pad, lat_max + lat_pad)

    ax.grid(True, which="major", alpha=0.3, linestyle="-", linewidth=1.5)

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}ms"))

    ax.invert_xaxis()
    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.grid(True, which="major", alpha=0.6, linestyle="-", linewidth=1.5)
    ax.grid(True, which="minor", alpha=0.3, linestyle="-", linewidth=1.5)

    plot_path = os.path.join(save_folder, "wer_vs_latency_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    return fig


def _plot_error_rate_size_grid(save_folder: str, show: bool):
    fig, ax = plt.subplots(figsize=(10, 8))

    engines = [e for e in SIZE if e in StreamingEngines and e in WER_EN]

    error_rates = []
    sizes = []
    colors = []
    for e in engines:
        error_rates.append(round(sum(w for w in WER_EN[e].values()) / len(WER_EN[e]) + 1e-9, 1))
        sizes.append(SIZE[e])
        colors.append(ENGINE_COLORS[e])

    ax.scatter(error_rates, sizes, color=colors, s=150, alpha=0.8, edgecolors="black", linewidth=2)

    for i, engine in enumerate(engines):
        y_offset = 20

        ax.annotate(
            ENGINE_PRINT_NAMES[engine],
            (error_rates[i], sizes[i]),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=9,
            color=colors[i],
            weight="bold",
        )

    ax.set_xlabel("Word Error Rate", fontsize=12)
    ax.set_ylabel("Model Size (MB)", fontsize=12)

    wer_min = min(error_rates)
    wer_max = max(error_rates)
    wer_pad = max((wer_max - wer_min) * 0.15, 1)
    ax.set_xlim(wer_min - wer_pad, wer_max + wer_pad)

    ax.set_yscale("log")
    ax.set_ylim(10, 10000)
    ax.yaxis.set_major_locator(plt.FixedLocator([10, 100, 1000, 10000]))

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f} MB"))

    ax.invert_xaxis()
    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.grid(True, which="major", alpha=0.6, linestyle="-", linewidth=1.5)
    ax.grid(True, which="minor", alpha=0.3, linestyle="-", linewidth=1.5)

    plot_path = os.path.join(save_folder, "wer_vs_size_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    return fig


def _plot_error_rate_core_hour_grid(save_folder: str, show: bool):
    fig, ax = plt.subplots(figsize=(10, 8))

    engines = [e for e in RTF if e in StreamingEngines and e in WER_EN]

    error_rates = []
    core_hours = []
    colors = []
    for e in engines:
        error_rates.append(round(sum(w for w in WER_EN[e].values()) / len(WER_EN[e]) + 1e-9, 1))
        core_hours.append(RTF[e][Datasets.LIBRI_SPEECH_TEST_CLEAN])
        colors.append(ENGINE_COLORS[e])

    ax.scatter(error_rates, core_hours, color=colors, s=150, alpha=0.8, edgecolors="black", linewidth=2)

    for i, engine in enumerate(engines):
        y_offset = 20

        ax.annotate(
            ENGINE_PRINT_NAMES[engine],
            (error_rates[i], core_hours[i]),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=9,
            color=colors[i],
            weight="bold",
        )

    ax.set_xlabel("Word Error Rate", fontsize=12)
    ax.set_ylabel("Core-Hour", fontsize=12)

    wer_min = min(error_rates)
    wer_max = max(error_rates)
    wer_pad = max((wer_max - wer_min) * 0.15, 1)
    ax.set_xlim(wer_min - wer_pad, wer_max + wer_pad)

    ax.set_yscale("log")
    ax.set_ylim(0.01, 10)
    ax.yaxis.set_major_locator(plt.FixedLocator([0.01, 0.1, 1, 10]))

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:g}"))

    ax.invert_xaxis()
    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.grid(True, which="major", alpha=0.6, linestyle="-", linewidth=1.5)
    ax.grid(True, which="minor", alpha=0.3, linestyle="-", linewidth=1.5)

    plot_path = os.path.join(save_folder, "wer_vs_core_hour_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    return fig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    save_folder = os.path.join(RESULTS_FOLDER, "plots")

    _plot_error_rate(WER_EN, save_path=os.path.join(save_folder, "WER.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_EN, save_path=os.path.join(save_folder, "WER_ST.png"), streaming=True, show=args.show)
    _plot_error_rate(WER_FR, save_path=os.path.join(save_folder, "WER_FR.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_FR, save_path=os.path.join(save_folder, "WER_FR_ST.png"), streaming=True, show=args.show)
    _plot_error_rate(WER_DE, save_path=os.path.join(save_folder, "WER_DE.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_DE, save_path=os.path.join(save_folder, "WER_DE_ST.png"), streaming=True, show=args.show)
    _plot_error_rate(WER_ES, save_path=os.path.join(save_folder, "WER_ES.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_ES, save_path=os.path.join(save_folder, "WER_ES_ST.png"), streaming=True, show=args.show)
    _plot_error_rate(WER_IT, save_path=os.path.join(save_folder, "WER_IT.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_IT, save_path=os.path.join(save_folder, "WER_IT_ST.png"), streaming=True, show=args.show)
    _plot_error_rate(WER_PT, save_path=os.path.join(save_folder, "WER_PT.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_PT, save_path=os.path.join(save_folder, "WER_PT_ST.png"), streaming=True, show=args.show)

    _plot_error_rate(
        PER_EN, save_path=os.path.join(save_folder, "PER_ST.png"), streaming=True, punctuation=True, show=args.show
    )
    _plot_error_rate(PER_FR, save_path=os.path.join(save_folder, "PER_FR_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_DE, save_path=os.path.join(save_folder, "PER_DE_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_ES, save_path=os.path.join(save_folder, "PER_ES_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_IT, save_path=os.path.join(save_folder, "PER_IT_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_PT, save_path=os.path.join(save_folder, "PER_PT_ST.png"), streaming=True, punctuation=True, show=args.show)

    _plot_cpu(save_folder=save_folder, show=args.show, dataset=Datasets.LIBRI_SPEECH_TEST_CLEAN)

    _plot_latency(save_folder=save_folder, show=args.show, dataset=Datasets.LIBRI_SPEECH_TEST_CLEAN)

    _plot_error_rate_latency_grid(save_folder, show=args.show)

    _plot_error_rate_size_grid(save_folder, show=args.show)

    _plot_error_rate_core_hour_grid(save_folder, show=args.show)


if __name__ == "__main__":
    main()
