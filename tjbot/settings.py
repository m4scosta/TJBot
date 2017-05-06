import os

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
QUESTIONS_DIR = os.path.join(PROJECT_DIR, 'questions')
DB_NAME = 'tjbot'
API_KEY = os.environ['TJBOT_API_KEY']
DB_HOST = os.environ['TJBOT_DB_HOST']
AUTO_QUESTION_TIME = os.environ['TJBOT_AUTO_QUESTION_TIME']

VALIDATE_ANSWER_REQUEST = 1
MATERIA_QUESTION_REQUEST = 2
