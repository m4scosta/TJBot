import json
import settings
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


DEFAULT_ALTERNATIVES = ('A', 'B', 'C', 'D', 'E')


def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def _build_button(label, **data):
    return InlineKeyboardButton(label, callback_data=json.dumps(data))


def _build_keyboard(btns_data, columns=2):
    buttons = map(lambda d: _build_button(d['label'], **d['data']), btns_data)
    rows = _chunks(buttons, columns)
    return InlineKeyboardMarkup(rows)


def _format_question_data(question, alternatives=DEFAULT_ALTERNATIVES):
    data = []
    for alternative in alternatives:
        data.append({
            'label': alternative,
            'data': {
                't': settings.VALIDATE_ANSWER_REQUEST,
                'qid': str(question.id),
                'alt': alternative
            }
        })
    return data


def _format_materia_data(materia):
    return {
        'label': materia.nome,
        'data': {
            't': settings.MATERIA_QUESTION_REQUEST,
            'mid': str(materia.id)
        }
    }


class KeyboardBuilder(object):

    @staticmethod
    def answer_keyboard(question):
        data = _format_question_data(question)
        return _build_keyboard(data)

    @staticmethod
    def materias_keyboard(*materias):
        data = map(_format_materia_data, materias)
        return _build_keyboard(data)
