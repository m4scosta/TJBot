from mongoengine import *


class Materia(Document):
    nome = StringField(required=True, unique=True)


class Questao(Document):
    prova = StringField(required=True)
    enunciado = StringField(required=True)
    alternativas = DictField(required=True)
    resposta = StringField(required=True, max_lenght=1)
    materia = ReferenceField(Materia)


class User(Document):
    telegram_id = LongField(required=True)
    chat_id = LongField(required=True)
    questao_automatica_ativa = BooleanField(default=False)
    respondidas = ListField(ReferenceField(Questao))
    acertos = ListField(ReferenceField(Questao))
    erros = ListField(ReferenceField(Questao))

    meta = {
        'indexes': [
            'telegram_id',
        ],
    }
