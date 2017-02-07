# coding: utf-8
import logging
import json
import random
import schedule
import time
import threading
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
    chat_id = update.message.chat.id
    if not User.objects(telegram_id=user.id):
        User(telegram_id=user.id, chat_id=chat_id).save()
    else:
        User(chat_id=chat_id)
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


def sortear_questao(user):
    nao_acertos = Questao.objects(id__nin=[q.id for q in user.acertos])
    random_index = random.choice(range(nao_acertos.count()))
    return nao_acertos[random_index]


def perguntar(bot, update):
    telegram_user = update.message.from_user
    user = User.objects.get(telegram_id=telegram_user.id)
    questao = sortear_questao(user)
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
            reply_markup = build_reply_markup(str(questao.id))
            bot.sendMessage(text=text,
                            reply_markup=reply_markup,
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
    dp.add_handler(
        CommandHandler("ativar_questao_automatica", ativar_questao_automatica))
    dp.add_handler(
        CommandHandler(
            "desativar_questao_automatica", desativar_questao_automatica))
    dp.add_handler(CallbackQueryHandler(validar_resposta))
    dp.add_error_handler(error)
    updater.start_polling()
    thread = threading.Thread(target=scheduler_task)
    thread.daemon = True
    thread.start()
    updater.idle()


if __name__ == '__main__':
    main()
