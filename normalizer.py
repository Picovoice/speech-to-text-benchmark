import re
import string
import unicodedata

import inflect

from languages import Languages


class Normalizer(object):
    @staticmethod
    def normalize(sentence: str, raise_error_on_invalid_sentence: bool) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, language: Languages):
        if language == Languages.EN:
            return EnglishNormalizer()
        elif language in [
            Languages.DE,
            Languages.ES,
            Languages.FR,
            Languages.IT,
            Languages.PT_PT,
            Languages.PT_BR,
        ]:
            return DefaultNormalizer()
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{language}`")


class DefaultNormalizer:
    """
    Adapted from: https://github.com/openai/whisper/blob/main/whisper/normalizers/basic.py
    """

    ADDITIONAL_DIACRITICS = {
        "œ": "oe",
        "Œ": "OE",
        "ø": "o",
        "Ø": "O",
        "æ": "ae",
        "Æ": "AE",
        "ß": "ss",
        "ẞ": "SS",
        "đ": "d",
        "Đ": "D",
        "ð": "d",
        "Ð": "D",
        "þ": "th",
        "Þ": "th",
        "ł": "l",
        "Ł": "L",
    }

    @staticmethod
    def _remove_symbols_and_diacritics(s: str) -> str:
        return "".join(
            (
                DefaultNormalizer.ADDITIONAL_DIACRITICS[c]
                if c in DefaultNormalizer.ADDITIONAL_DIACRITICS
                else (
                    ""
                    if unicodedata.category(c) == "Mn"
                    else " " if unicodedata.category(c)[0] in "MSP" else c
                )
            )
            for c in unicodedata.normalize("NFKD", s)
        )

    @staticmethod
    def normalize(sentence: str, raise_error_on_invalid_sentence: bool = False) -> str:
        sentence = sentence.lower()
        sentence = re.sub(r"[<\[][^>\]]*[>\]]", "", sentence)
        sentence = re.sub(r"\(([^)]+?)\)", "", sentence)
        sentence = DefaultNormalizer._remove_symbols_and_diacritics(sentence).lower()
        sentence = re.sub(r"\s+", " ", sentence)

        return sentence


class EnglishNormalizer(Normalizer):
    AMERICAN_SPELLINGS = {
        "acknowledgement": "acknowledgment",
        "analogue": "analog",
        "armour": "armor",
        "ascendency": "ascendancy",
        "behaviour": "behavior",
        "behaviourist": "behaviorist",
        "cancelled": "canceled",
        "catalogue": "catalog",
        "centre": "center",
        "centres": "centers",
        "colour": "color",
        "coloured": "colored",
        "colourist": "colorist",
        "colourists": "colorists",
        "colours": "colors",
        "cosier": "cozier",
        "counselled": "counseled",
        "criticised": "criticized",
        "crystallise": "crystallize",
        "defence": "defense",
        "discoloured": "discolored",
        "dishonour": "dishonor",
        "dishonoured": "dishonored",
        "encyclopaedia": "Encyclopedia",
        "endeavour": "endeavor",
        "endeavouring": "endeavoring",
        "favour": "favor",
        "favourite": "favorite",
        "favours": "favors",
        "fibre": "fiber",
        "flamingoes": "flamingos",
        "fulfill": "fulfil",
        "grey": "gray",
        "harmonised": "harmonized",
        "honour": "honor",
        "honourable": "honorable",
        "honourably": "honorably",
        "honoured": "honored",
        "honours": "honors",
        "humour": "humor",
        "islamised": "islamized",
        "labour": "labor",
        "labourers": "laborers",
        "levelling": "leveling",
        "luis": "lewis",
        "lustre": "luster",
        "manoeuvring": "maneuvering",
        "marshall": "marshal",
        "marvellous": "marvelous",
        "merchandising": "merchandizing",
        "milicent": "millicent",
        "moustache": "mustache",
        "moustaches": "mustaches",
        "neighbour": "neighbor",
        "neighbourhood": "neighborhood",
        "neighbouring": "neighboring",
        "neighbours": "neighbors",
        "omelette": "omelet",
        "organisation": "organization",
        "organiser": "organizer",
        "practise": "practice",
        "pretence": "pretense",
        "programme": "program",
        "realise": "realize",
        "realised": "realized",
        "recognised": "recognized",
        "shrivelled": "shriveled",
        "signalling": "signaling",
        "skilfully": "skillfully",
        "smouldering": "smoldering",
        "specialised": "specialized",
        "sterilise": "sterilize",
        "sylvia": "silvia",
        "theatre": "theater",
        "theatres": "theaters",
        "travelled": "traveled",
        "travellers": "travelers",
        "travelling": "traveling",
        "vapours": "vapors",
        "wilful": "willful",
    }

    ABBREVIATIONS = {
        "junior": "jr",
        "senior": "sr",
        "okay": "ok",
        "doctor": "dr",
        "mister": "mr",
        "missus": "mrs",
        "saint": "st",
    }

    @staticmethod
    def to_american(sentence: str) -> str:
        return " ".join(
            [
                (
                    EnglishNormalizer.AMERICAN_SPELLINGS[x]
                    if x in EnglishNormalizer.AMERICAN_SPELLINGS
                    else x
                )
                for x in sentence.split()
            ]
        )

    @staticmethod
    def normalize_abbreviations(sentence: str) -> str:
        return " ".join(
            [
                (
                    EnglishNormalizer.ABBREVIATIONS[x]
                    if x in EnglishNormalizer.ABBREVIATIONS
                    else x
                )
                for x in sentence.split()
            ]
        )

    @staticmethod
    def normalize(sentence: str, raise_error_on_invalid_sentence: bool = False) -> str:
        p = inflect.engine()

        sentence = sentence.lower()

        for c in "-/–—":
            sentence = sentence.replace(c, " ")

        for c in '‘!",.:;?“”`':
            sentence = sentence.replace(c, "")

        sentence = sentence.replace("’", "'").replace("&", "and")

        def num2txt(y):
            return (
                p.number_to_words(y).replace("-", " ").replace(",", "")
                if any(x.isdigit() for x in y)
                else y
            )

        sentence = " ".join(num2txt(x) for x in sentence.split())

        if raise_error_on_invalid_sentence:
            if not all(c in " '" + string.ascii_lowercase for c in sentence):
                raise RuntimeError()
            if any(x.startswith("'") for x in sentence.split()):
                raise RuntimeError()

        return sentence


__all__ = ["Normalizer"]
