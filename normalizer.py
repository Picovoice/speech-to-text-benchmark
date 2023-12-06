import string

import inflect


class Normalizer:
    AMERICAN_SPELLINGS = {
        'acknowledgement': 'acknowledgment',
        'analogue': 'analog',
        'armour': 'armor',
        'ascendency': 'ascendancy',
        'behaviour': 'behavior',
        'behaviourist': 'behaviorist',
        'cancelled': 'canceled',
        'catalogue': 'catalog',
        'centre': 'center',
        'centres': 'centers',
        'colour': 'color',
        'coloured': 'colored',
        'colourist': 'colorist',
        'colourists': 'colorists',
        'colours': 'colors',
        'cosier': 'cozier',
        'counselled': 'counseled',
        'criticised': 'criticized',
        'crystallise': 'crystallize',
        'defence': 'defense',
        'discoloured': 'discolored',
        'dishonour': 'dishonor',
        'dishonoured': 'dishonored',
        'encyclopaedia': 'Encyclopedia',
        'endeavour': 'endeavor',
        'endeavouring': 'endeavoring',
        'favour': 'favor',
        'favourite': 'favorite',
        'favours': 'favors',
        'fibre': 'fiber',
        'flamingoes': 'flamingos',
        'fulfill': 'fulfil',
        'grey': 'gray',
        'harmonised': 'harmonized',
        'honour': 'honor',
        'honourable': 'honorable',
        'honourably': 'honorably',
        'honoured': 'honored',
        'honours': 'honors',
        'humour': 'humor',
        'islamised': 'islamized',
        'labour': 'labor',
        'labourers': 'laborers',
        'levelling': 'leveling',
        'luis': 'lewis',
        'lustre': 'luster',
        'manoeuvring': 'maneuvering',
        'marshall': 'marshal',
        'marvellous': 'marvelous',
        'merchandising': 'merchandizing',
        'milicent': 'millicent',
        'moustache': 'mustache',
        'moustaches': 'mustaches',
        'neighbour': 'neighbor',
        'neighbourhood': 'neighborhood',
        'neighbouring': 'neighboring',
        'neighbours': 'neighbors',
        'omelette': 'omelet',
        'organisation': 'organization',
        'organiser': 'organizer',
        'practise': 'practice',
        'pretence': 'pretense',
        'programme': 'program',
        'realise': 'realize',
        'realised': 'realized',
        'recognised': 'recognized',
        'shrivelled': 'shriveled',
        'signalling': 'signaling',
        'skilfully': 'skillfully',
        'smouldering': 'smoldering',
        'specialised': 'specialized',
        'sterilise': 'sterilize',
        'sylvia': 'silvia',
        'theatre': 'theater',
        'theatres': 'theaters',
        'travelled': 'traveled',
        'travellers': 'travelers',
        'travelling': 'traveling',
        'vapours': 'vapors',
        'willful': 'wilful',
        'wylder': 'wilder',
    }

    ABBREVIATIONS = {
        'junior': 'jr',
        'senior': 'sr',
        'okay': 'ok',
        'doctor': 'dr',
        'drive': 'dr',
        'mr': 'mister',
        'mrs': 'missus',
        'saint': 'st',
    }

    def _to_american(self, sentence: str) -> str:
        return ' '.join([self.AMERICAN_SPELLINGS[x] if x in self.AMERICAN_SPELLINGS else x for x in sentence.split()])

    def _normalize_abbreviations(self, sentence: str) -> str:
        return ' '.join([self.ABBREVIATIONS[x] if x in self.ABBREVIATIONS else x for x in sentence.split()])

    def normalize(self, sentence: str) -> str:
        p = inflect.engine()

        sentence = sentence.lower()

        for c in '-/–—':
            sentence = sentence.replace(c, ' ')

        for c in '‘!",.:;?“”`':
            sentence = sentence.replace(c, '')

        sentence = sentence.replace("’", "'").replace('&', 'and')

        def num2txt(y):
            return p.number_to_words(y).replace('-', ' ').replace(',', '') if any(x.isdigit() for x in y) else y

        sentence = ' '.join(num2txt(x) for x in sentence.split())

        if not all(c in " '" + string.ascii_lowercase for c in sentence):
            raise RuntimeError()
        if any(x.startswith("'") for x in sentence.split()):
            raise RuntimeError()

        sentence = self._to_american(sentence)
        sentence = self._normalize_abbreviations(sentence)

        return sentence


__all__ = ['Normalizer']
