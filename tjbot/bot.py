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
from template_helper import render
import settings

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Setup questoes **temporario**
PROJECT_DIR = path.dirname(path.dirname(__file__))

with open(path.join(PROJECT_DIR, 'questoes.json')) as f:
    QUESTOES = json.loads(f.read())


def start(bot, update):
    user = update.message.from_user.first_name
    update.message.reply_text(render('start.tpl', user=user))


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
    questao_id = random.choice(range(len(QUESTOES)))
    questao = QUESTOES[questao_id]
    reply_markup = build_reply_markup(questao_id)
    message_text = render('questao.tpl', **questao)
    update.message.reply_text(message_text,
                              reply_markup=reply_markup,
                              parse_mode='html')


def validar_resposta(bot, update):
    query = update.callback_query
    data = json.loads(query.data)

    questao = QUESTOES[data['questao_id']]
    resposta = questao['resposta']

    # TODO: contabilizar acerto para contato
    text = render('questao.tpl', **questao)
    if data['alternativa'] == resposta:
        text += u"\n\nResposta certa, parabéns!"
    else:
        text += u"\n\nVocê errou :(\nResposta certa: %s" % resposta

    bot.editMessageText(text=text,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        parse_mode='html')


def estatisticas(bot, update):
    # TODO: armazenar contato
    # TODO: calcular estatisticas com dados do contato
    reply = 'Respondidas: 50\nAcertos: 39(78%)\nErros: 11(22%)'
    update.message.reply_text(reply)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
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
# TODO: criar comando de estatisticas(acertos, erros, total, aproveitamento)
