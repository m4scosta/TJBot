# coding: utf-8
import logging
import json
import random
import schedule
import time
import threading
import settings
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from storage import connect_to_database
from models import User, Questao, Materia
from template_helper import render
from keyboards import KeyboardBuilder
from commands.clear_data import ClearData

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(bot, update):
    user = update.message.from_user
    chat_id = update.message.chat.id
    if not User.objects(telegram_id=user.id):
        User(telegram_id=user.id, chat_id=chat_id).save()
    else:
        User(chat_id=chat_id)
    update.message.reply_text(render('start.tpl', user=user.first_name))


def help(bot, update):
    user = update.message.from_user.first_name
    update.message.reply_text(render('help.tpl', user=user))


def sortear_questao(user, materia=None):
    query = {'id__nin': [q.id for q in user.acertos]}
    if materia is not None:
        query['materia'] = materia
    nao_acertos = Questao.objects(**query)
    return random.choice(nao_acertos)


def perguntar(bot, update):
    telegram_user = update.message.from_user
    user = User.objects.get(telegram_id=telegram_user.id)
    materias = Materia.objects()
    message_text = 'Qual matéria?'
    keyboard = KeyboardBuilder.materias_keyboard(*materias)
    update.message.reply_text(message_text, reply_markup=keyboard)


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
        questao = sortear_questao(user, materia=data['mid'])
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


def estatisticas(bot, update):
    telegram_user = update.message.from_user
    user = User.objects.get(telegram_id=telegram_user.id)
    respondidas = len(user.respondidas)
    acertos = len(user.acertos)
    erros = len(user.erros)
    context = {
        'respondidas': respondidas,
        'acertos': acertos,
        'acertos_porcent': acertos * 100. / max(respondidas, 1),
        'erros': erros,
        'erros_porcent': erros * 100. / max(respondidas, 1)
    }
    reply = render('estatisticas.tpl', **context)
    update.message.reply_text(reply, parse_mode='html')


def ativar_questao_automatica(bot, update):
    telegram_user = update.message.from_user
    user = User.objects.get(telegram_id=telegram_user.id)
    if not user.questao_automatica_ativa:
        user.questao_automatica_ativa = True
        user.save()
    update.message.reply_text('Questão automática ativada com sucesso.')


def desativar_questao_automatica(bot, update):
    telegram_user = update.message.from_user
    user = User.objects.get(telegram_id=telegram_user.id)
    if user.questao_automatica_ativa:
        user.questao_automatica_ativa = False
        user.save()
        reply = 'Questão automática desativada com sucesso.'
    else:
        reply = 'Questão automática não está ativa, nada feito.'
    update.message.reply_text(reply)


def enviar_questao_automatica(bot):
    def task():
        users = User.objects(questao_automatica_ativa=True)
        for user in users:
            questao = sortear_questao(user)
            text = render('questao.tpl', questao=questao)
            keyboard = KeyboardBuilder.answer_keyboard(questao)
            bot.sendMessage(text=text,
                            reply_markup=keyboard,
                            chat_id=user.chat_id,
                            parse_mode='html')
    return task


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def scheduler_task():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    connect_to_database()
    updater = Updater(settings.API_KEY)
    schedule.every().day.at(settings.AUTO_QUESTION_TIME).do(
        enviar_questao_automatica(updater.bot))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("perguntar", perguntar))
    dp.add_handler(CommandHandler("estatisticas", estatisticas))
    dp.add_handler(CommandHandler("limpar_dados", ClearData()))
    dp.add_handler(
        CommandHandler("ativar_questao_automatica", ativar_questao_automatica))
    dp.add_handler(
        CommandHandler(
            "desativar_questao_automatica", desativar_questao_automatica))
    dp.add_handler(CallbackQueryHandler(QueryHandler()))
    dp.add_error_handler(error)
    updater.start_polling()
    thread = threading.Thread(target=scheduler_task)
    thread.daemon = True
    thread.start()
    updater.idle()


if __name__ == '__main__':
    main()
