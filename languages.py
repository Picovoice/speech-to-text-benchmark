from enum import Enum


class Languages(Enum):
    EN = "EN"
    DE = "DE"
    ES = "ES"
    FR = "FR"
    IT = "IT"
    PT_PT = "PT-PT"
    PT_BR = "PT-BR"


LANGUAGE_TO_CODE = {
    Languages.EN: "en-US",
    Languages.DE: "de-DE",
    Languages.ES: "es-ES",
    Languages.FR: "fr-FR",
    Languages.IT: "it-IT",
    Languages.PT_PT: "pt-PT",
    Languages.PT_BR: "pt-BR",
}

__all__ = [
    "LANGUAGE_TO_CODE",
    "Languages",
]
