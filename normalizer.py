import re
import string
import unicodedata
from typing import (
    List,
    Optional
)

import inflect
import num2words

from languages import Languages

SUPPORTED_PUNCTUATION_SET = ",.?、。？"


class Normalizer(object):
    def __init__(self, keep_punctuation: bool, punctuation_set: str = SUPPORTED_PUNCTUATION_SET) -> None:
        self._keep_punctuation = keep_punctuation
        self._punctuation_set = punctuation_set

    def normalize(self, sentence: str, raise_error_on_invalid_sentence: bool) -> str:
        raise NotImplementedError()

    @classmethod
    def create(
        cls,
        language: Languages,
        keep_punctuation: bool,
        punctuation_set: str = SUPPORTED_PUNCTUATION_SET,
    ):
        if language == Languages.EN:
            return EnglishNormalizer(keep_punctuation, punctuation_set)
        elif language == Languages.JA:
            return JapaneseNormalizer(keep_punctuation, punctuation_set)
        elif language == Languages.KO:
            return KoreanNormalizer(keep_punctuation, punctuation_set)
        elif language in [
            Languages.DE,
            Languages.ES,
            Languages.FR,
            Languages.IT,
            Languages.PT_PT,
            Languages.PT_BR,
        ]:
            return DefaultNormalizer(keep_punctuation, punctuation_set)
        else:
            raise ValueError(f"Cannot create {cls.__name__} of type `{language}`")


class DefaultNormalizer(Normalizer):
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

    def _remove_symbols_and_diacritics(self, s: str) -> str:
        return "".join(
            (
                DefaultNormalizer.ADDITIONAL_DIACRITICS[c]
                if c in DefaultNormalizer.ADDITIONAL_DIACRITICS
                else (
                    ""
                    if unicodedata.category(c) == "Mn"
                    else (
                        " "
                        if unicodedata.category(c)[0] in "MS"
                        or (unicodedata.category(c)[0] == "P" and c not in SUPPORTED_PUNCTUATION_SET)
                        else c
                    )
                )
            )
            for c in unicodedata.normalize("NFKD", s)
        )

    def normalize(self, sentence: str, raise_error_on_invalid_sentence: bool = False) -> str:
        sentence = sentence.lower()
        sentence = re.sub(r"[<\[][^>\]]*[>\]]", "", sentence)
        sentence = re.sub(r"\(([^)]+?)\)", "", sentence)
        sentence = sentence.replace("!", ".")
        sentence = sentence.replace("...", "")
        sentence = self._remove_symbols_and_diacritics(sentence).lower()

        if self._keep_punctuation:
            removable_punctuation = "".join(set(SUPPORTED_PUNCTUATION_SET) - set(self._punctuation_set))
        else:
            removable_punctuation = SUPPORTED_PUNCTUATION_SET

        for c in removable_punctuation:
            sentence = sentence.replace(c, "")

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

    APOSTROPHE_REGEX = r"(?<!\w)\'|\'(?!\w)"  # Apostrophes that are not part of a contraction

    @staticmethod
    def to_american(sentence: str) -> str:
        return " ".join(
            [
                (EnglishNormalizer.AMERICAN_SPELLINGS[x] if x in EnglishNormalizer.AMERICAN_SPELLINGS else x)
                for x in sentence.split()
            ]
        )

    @staticmethod
    def normalize_abbreviations(sentence: str) -> str:
        return " ".join(
            [
                (EnglishNormalizer.ABBREVIATIONS[x] if x in EnglishNormalizer.ABBREVIATIONS else x)
                for x in sentence.split()
            ]
        )

    @staticmethod
    def strip_accents(sentence: str) -> str:
        decomposed = unicodedata.normalize("NFD", sentence)
        return "".join(c for c in decomposed if not unicodedata.combining(c))

    def normalize(self, sentence: str, raise_error_on_invalid_sentence: bool = False) -> str:
        p = inflect.engine()

        sentence = sentence.lower()

        sentence = self.strip_accents(sentence)

        for c in "-/–—":
            sentence = sentence.replace(c, " ")

        for c in '‘":;“”`()[]':
            sentence = sentence.replace(c, "")

        sentence = sentence.replace("!", ".")
        sentence = sentence.replace("...", "")
        sentence = sentence.replace("…", "")

        if self._keep_punctuation:
            removable_punctuation = "".join(set(SUPPORTED_PUNCTUATION_SET) - set(self._punctuation_set))
        else:
            removable_punctuation = SUPPORTED_PUNCTUATION_SET

        for c in removable_punctuation:
            sentence = sentence.replace(c, "")

        sentence = sentence.replace("’", "'").replace("&", "and")

        sentence = re.sub(self.APOSTROPHE_REGEX, "", sentence)

        def num2txt(y):
            if any(x.isdigit() for x in y):
                ends_with_period = y[-1] == '.' and self._keep_punctuation
                if ends_with_period:
                    y = y[:-1]
                y = p.number_to_words(y).replace("-", " ").replace(",", "")
                if ends_with_period:
                    y += '.'
            return y

        sentence = " ".join(num2txt(x) for x in sentence.split())

        if raise_error_on_invalid_sentence:
            valid_characters = " '" + self._punctuation_set if self._keep_punctuation else " '"
            if not all(c in valid_characters + string.ascii_lowercase for c in sentence):
                raise RuntimeError()
            if any(x.startswith("'") for x in sentence.split()):
                raise RuntimeError()

        return sentence


class JapaneseNormalizer(Normalizer):
    def __init__(self, keep_punctuation: bool, punctuation_set: str = SUPPORTED_PUNCTUATION_SET) -> None:
        super().__init__(keep_punctuation, punctuation_set)
        self._number_re = re.compile(r"\d+(?:\.\d+)?")

    def _normalize_numbers(self, text: str) -> str:
        def convert(match: "re.Match[str]") -> str:
            token = match.group(0)
            try:
                value = float(token) if "." in token else int(token)
                return num2words.num2words(value, lang='ja')
            except OverflowError:
                return token

        return self._number_re.sub(convert, text)

    def _expand_repeater(self, text: str) -> str:
        res: List[str] = []
        for ch in text:
            if ch == "々" and res:
                res.append(res[-1])
            else:
                res.append(ch)
        return "".join(res)

    def _strip_punct_space(self, text: str) -> str:
        chars: List[str] = []
        for ch in text:
            category = unicodedata.category(ch)
            if ch.isspace() or category.startswith("Z"):
                continue
            if category.startswith("P"):
                if self._keep_punctuation and ch in self._punctuation_set:
                    chars.append(ch)
                continue
            chars.append(ch)
        return "".join(chars)

    @staticmethod
    def _is_japanese_char(ch: str) -> bool:
        code = ord(ch)
        if 0x3040 <= code <= 0x309F:      # Hiragana
            return True
        if 0x30A0 <= code <= 0x30FF:      # Katakana
            return True
        if 0x31F0 <= code <= 0x31FF:      # Katakana Phonetic Extensions
            return True
        if 0x4E00 <= code <= 0x9FFF:      # CJK Unified Ideographs
            return True
        if 0x3400 <= code <= 0x4DBF:      # CJK Extension A
            return True
        if 0x20000 <= code <= 0x3134F:    # CJK Extensions B-G
            return True
        if 0xF900 <= code <= 0xFAFF:      # CJK Compatibility Ideographs
            return True
        if ch in {"々", "〆", "〇", "ヶ", "ゝ", "ゞ", "ヽ", "ヾ"}:
            return True
        return False

    def _is_allowed_char(self, ch: str) -> bool:
        if self._is_japanese_char(ch):
            return True
        if self._keep_punctuation and ch in self._punctuation_set:
            return True
        return False

    def _validate(self, text: str, original: str) -> None:
        invalid = [(i, ch) for i, ch in enumerate(text) if not self._is_allowed_char(ch)]
        if invalid:
            details = ", ".join(
                f"index={i}, char={ch!r}, U+{ord(ch):04X}, "
                f"name={unicodedata.name(ch, 'UNKNOWN')}, "
                f"category={unicodedata.category(ch)}"
                for i, ch in invalid
            )
            raise RuntimeError(
                "Disallowed character(s) after normalization: "
                f"{details}. Original: {original!r}. Cleaned: {text!r}"
            )

    def normalize(
        self,
        sentence: Optional[str],
        raise_error_on_invalid_sentence: bool = False,
    ) -> str:
        if sentence is None:
            if raise_error_on_invalid_sentence:
                raise ValueError("Input text is None.")
            return ""

        original = str(sentence)
        text = unicodedata.normalize("NFKC", original)

        text = self._normalize_numbers(text)

        text = self._expand_repeater(text)

        text = self._strip_punct_space(text)

        if raise_error_on_invalid_sentence:
            self._validate(text, original)

        return text


class KoreanNormalizer(Normalizer):
    def __init__(self, keep_punctuation: bool, punctuation_set: str = SUPPORTED_PUNCTUATION_SET) -> None:
        super().__init__(keep_punctuation, punctuation_set)
        self._korean_regex = re.compile(rf"^[가-힣\s{punctuation_set}]+$")

    def normalize(self, sentence: str, raise_error_on_invalid_sentence: bool = False) -> str:
        sentence = unicodedata.normalize("NFC", sentence)
        sentence = re.sub(r"[<\[][^>\]]*[>\]]", "", sentence)
        sentence = re.sub(r"\(([^)]+?)\)", "", sentence)
        sentence = sentence.replace("!", ".")
        sentence = sentence.replace("...", "")

        if self._keep_punctuation:
            removable_punctuation = "".join(set(SUPPORTED_PUNCTUATION_SET) - set(self._punctuation_set))
        else:
            removable_punctuation = SUPPORTED_PUNCTUATION_SET

        for c in removable_punctuation:
            sentence = sentence.replace(c, "")

        sentence = re.sub(r"\s+", " ", sentence)

        if raise_error_on_invalid_sentence:
            if not bool(self._korean_regex.fullmatch(sentence)):
                raise RuntimeError()

        return sentence


__all__ = [
    "Normalizer",
]
