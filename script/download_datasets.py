import argparse
import os
import tarfile

from huggingface_hub import snapshot_download

from dataset import Datasets
from languages import Languages

DATASET_TO_LANGUAGES = {
    Datasets.FLEURS: [
        Languages.EN,
        Languages.FR,
        Languages.DE,
        Languages.ES,
        Languages.IT,
        Languages.KO,
        Languages.JA,
        Languages.PT_BR,
    ],
    Datasets.JSUT_BASIC: [Languages.JA],
}


def _download_fleurs(language: Languages, download_folder: str) -> None:
    os.makedirs(download_folder, exist_ok=True)

    language_to_code = {
        Languages.EN: "en_us",
        Languages.FR: "fr_fr",
        Languages.DE: "de_de",
        Languages.ES: "es_419",
        Languages.IT: "it_it",
        Languages.KO: "ko_kr",
        Languages.JA: "ja_jp",
        Languages.PT_BR: "pt_br",
    }
    code = language_to_code[language]

    snapshot_download(
        repo_id="google/fleurs",
        repo_type="dataset",
        local_dir=download_folder,
        allow_patterns=[
            f"data/{code}/audio/test.tar.gz",
            f"data/{code}/test.tsv",
        ],
    )

    with tarfile.open(os.path.join(download_folder, "data", code, "audio", "test.tar.gz")) as tar:
        tar.extractall(path=os.path.join(download_folder, "data", code, "audio"), filter="data")


def _download_jsut_basic(download_folder: str) -> None:
    os.makedirs(download_folder, exist_ok=True)

    snapshot_download(
        repo_id="japanese-asr/ja_asr.jsut_basic5000",
        repo_type="dataset",
        local_dir=download_folder,
    )


def download_dataset(dataset: Datasets, language: Languages, download_folder: str) -> None:
    supported_languages = DATASET_TO_LANGUAGES[dataset]
    if language not in supported_languages:
        raise ValueError(
            f"{dataset.value} does not support language `{language.value}` "
            f"(supported: {[lang.value for lang in supported_languages]})"
        )

    if dataset is Datasets.FLEURS:
        _download_fleurs(language, download_folder)
    elif dataset is Datasets.JSUT_BASIC:
        _download_jsut_basic(download_folder)
    else:
        raise ValueError(f"{dataset.value} cannot be downloaded. Download the dataset from the link in the README.")

    print(f"Completed downloading {dataset.value} ({language.value})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=[dataset.value for dataset in DATASET_TO_LANGUAGES.keys()])
    parser.add_argument("--language", required=True, choices=[language.value for language in Languages])
    parser.add_argument("--download-folder", required=True)
    args = parser.parse_args()

    download_dataset(Datasets(args.dataset), Languages(args.language), args.download_folder)


if __name__ == "__main__":
    main()
