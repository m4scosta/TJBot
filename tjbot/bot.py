# coding: utf-8
import logging
import json
import random
import urllib
from os import path
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import settings
from template_helper import render
from storage import connect_to_database
from models import User
from models import Questao

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(bot, update):
    user = update.message.from_user
    if not User.objects(telegram_id=user.id):
        User(telegram_id=user.id).save()
    update.message.reply_text(render('start.tpl', user=user.first_name))


def help(bot, update):
    user = update.message.from_user.first_name
    update.message.reply_text(render('help.tpl', user=user))


def build_keyboard_button(questao_id, alternativa):
    data = json.dumps({'questao_id': questao_id, 'alternativa': alternativa})
    return InlineKeyboardButton(alternativa, callback_data=data)


def build_reply_markup(questao_id):
    a = build_keyboard_button(questao_id, "A")
    b = build_keyboard_button(questao_id, "B")
    c = build_keyboard_button(questao_id, "C")
    d = build_keyboard_button(questao_id, "D")
    e = build_keyboard_button(questao_id, "E")
    return InlineKeyboardMarkup([[a, b], [c, d], [e]])


def perguntar(bot, update):
    questao_idx = random.choice(range(Questao.objects().count()))
    questao = Questao.objects[questao_idx]
    reply_markup = build_reply_markup(str(questao.id))
    message_text = render('questao.tpl', questao=questao)
    update.message.reply_text(message_text,
                              reply_markup=reply_markup,
                              parse_mode='html')


def validar_resposta(bot, update):
    query = update.callback_query
    data = json.loads(query.data)

    user = User.objects(telegram_id=query.from_user.id)
    questao = Questao.objects.get(id=data['questao_id'])

    resposta = questao.resposta
    text = render('questao.tpl', questao=questao)

    if data['alternativa'] == resposta:
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
    acertos_porcent = acertos * 100. / respondidas
    erros = len(user.erros)
    erros_porcent = erros * 100. / respondidas
    reply = 'Respondidas: {}\nAcertos: {}({:.2f}%)\nErros: {}({:.2f}%)'.format(
        respondidas, acertos, acertos_porcent, erros, erros_porcent)
    update.message.reply_text(reply)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    connect_to_database()
    updater = Updater(settings.TJBOT_API_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("perguntar", perguntar))
    dp.add_handler(CommandHandler("estatisticas", estatisticas))
    dp.add_handler(CallbackQueryHandler(validar_resposta))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

# TODO: nao repetir questoes
# TODO: criar agendamento de perguntas
