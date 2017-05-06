# coding: utf-8
import os
import sys
import json
from mongoengine import connect
import settings
from models import Questao, Materia
from pprint import pprint


def connect_to_database():
    return connect(settings.DB_NAME, host=settings.DB_HOST)


def read_questions_from_json_file(fname):
    with open(os.path.join(settings.QUESTIONS_DIR, fname)) as f:
        return json.loads(f.read())


def find_or_create_materia(name):
    try:
        return Materia.objects.get(nome=name)
    except Exception:
        return Materia(nome=name).save()


def import_questions(fname, materia_name):
    """Usar com cautela"""
    connect_to_database()
    questions = read_questions_from_json_file(fname)
    materia = find_or_create_materia(materia_name)
    map(lambda q: q.update({'materia': materia.id}), questions)

    for q in questions:
       Questao(**q).save()


if __name__ == '__main__':
    pprint(read_questions_from_json_file('direito-penal.json'))
    # import_questions('direito-penal.json', 'Direito penal')
    # import_questions('direito-constitucional.json', 'Direito constitucional')
    # import_questions('direito-administrativo.json', 'Direito administrativo')
    # import_questions('portugues.json', 'Portugês')
    # import_questions('direito-processual-penal.json', 'Direito Processual penal')
