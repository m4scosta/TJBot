from os import path
import json
from mongoengine import connect
import settings
from models import Questao


def connect_to_database():
    return connect(settings.DB_NAME, host=settings.DB_HOST)


PROJECT_DIR = path.dirname(path.dirname(__file__))

def import_questoes():
    """Usar com cautela"""
    connect_to_database()
    with open(path.join(PROJECT_DIR, 'questoes.json')) as f:
        QUESTOES = json.loads(f.read())
    for q in QUESTOES:
        Questao(**q).save()


if __name__ == '__main__':
    import_questoes()
