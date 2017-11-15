# coding: utf-8
import json
import random
import settings
from commands.command_handler import CommandHandler
from models import Materia, Questao, User
from keyboards import KeyboardBuilder
from template_helper import render


def choose_question(user, materia=None):
    query = {'id__nin': [q.id for q in user.acertos]}
    if materia is not None:
        query['materia'] = materia
    nao_acertos = Questao.objects(**query)
    return random.choice(nao_acertos)


class AskQuestion(CommandHandler):

    def handle(self):
        themes = Materia.objects()
        keyboard = KeyboardBuilder.materias_keyboard(*themes)
        self.reply_text('Qual matéria?', reply_markup=keyboard)


class QueryHandler(object):

    def __call__(self, bot, update, **kwargs):
        query = update.callback_query
        data = json.loads(query.data)
        user = User.objects.get(telegram_id=query.from_user.id)
        request_type = data['t']

        if request_type == settings.MATERIA_QUESTION_REQUEST:
            self.send_materia_question(bot, update, query, data, user)
        elif request_type == settings.VALIDATE_ANSWER_REQUEST:
            self.validate_answer(bot, update, query, data, user)
        else:
            bot.editMessageText(text='Mensagem inválida.',
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    def send_materia_question(self, bot, update, query, data, user):
        questao = choose_question(user, materia=data['mid'])
        keyboard = KeyboardBuilder.answer_keyboard(questao)
        message_text = render('questao.tpl', questao=questao)
        bot.editMessageText(text=message_text,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            reply_markup=keyboard,
                            parse_mode='html')

    def validate_answer(self, bot, update, query, data, user):
        user = User.objects(id=user.id)  # must be QuerySet to allow update_one
        questao = Questao.objects.get(id=data['qid'])
        resposta = questao.resposta
        text = render('questao.tpl', questao=questao)

        if data['alt'] == resposta:
            user.update_one(push__acertos=questao)
            text += u"\n\n<b>Resposta certa, parabéns!</b>"
        else:
            user.update_one(push__erros=questao)
            text += u"\n\n<b>Você errou :(\nResposta certa: %s</b>" % resposta

        user.update_one(push__respondidas=questao)

        bot.editMessageText(text=text,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            parse_mode='html')
