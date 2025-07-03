import argparse
import os
import tarfile

from huggingface_hub import snapshot_download

from languages import Languages

LANGUAGE_TO_CODE = {
    Languages.EN: "en_us",
    Languages.FR: "fr_fr",
    Languages.DE: "de_de",
    Languages.ES: "es_419",
    Languages.IT: "it_it",
    Languages.PT_BR: "pt_br",
}


def download_language(language: Languages, download_folder: str) -> None:
    os.makedirs(download_folder, exist_ok=True)

    language_code = LANGUAGE_TO_CODE[language]

    snapshot_download(
        repo_id="google/fleurs",
        repo_type="dataset",
        local_dir=download_folder,
        allow_patterns=[
            f"data/{language_code}/audio/test.tar.gz",
            f"data/{language_code}/test.tsv",
        ],
    )

    with tarfile.open(os.path.join(download_folder, "data", language_code, "audio", "test.tar.gz")) as tar:
        tar.extractall(path=os.path.join(download_folder, "data", language_code, "audio"), filter="data")

    print(f"Completed downloading Fleurs {language.value}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--languages", required=True, nargs="+", choices=[x.value for x in LANGUAGE_TO_CODE.keys()])
    parser.add_argument("--download-folder", required=True)
    args = parser.parse_args()

    languages = args.languages
    download_folder = args.download_folder

    for language in languages:
        download_language(Languages(language), download_folder)


if __name__ == "__main__":
    main()
