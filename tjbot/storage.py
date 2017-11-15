# coding: utf-8
import os
import json
from mongoengine import connect
import settings
from models import Questao, Materia


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
    connect_to_database()
    questions = read_questions_from_json_file(fname)
    materia = find_or_create_materia(materia_name)
    map(lambda q: q.update({'materia': materia.id}), questions)
    for q in questions:
        Questao(**q).save()
