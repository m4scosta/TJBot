# coding: utf-8
import logging
import schedule
import time
import threading
import settings
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from storage import connect_to_database
from models import User
from template_helper import render
from keyboards import KeyboardBuilder
from commands.question import AskQuestion, QueryHandler, choose_question
from commands.clear_data import ClearData
from commands.start import Start
from commands.help import Help
from commands.statistics import Statistics
from commands.auto_question import EnableAutoQuestion, DisableAutoQuestion


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def enviar_questao_automatica(bot):
    def task():
        users = User.objects(questao_automatica_ativa=True)
        for user in users:
            questao = choose_question(user)
            text = render('questao.tpl', questao=questao)
            keyboard = KeyboardBuilder.answer_keyboard(questao)
            bot.sendMessage(text=text,
                            reply_markup=keyboard,
                            chat_id=user.chat_id,
                            parse_mode='html')
    return task


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def task_runner():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    connect_to_database()
    updater = Updater(settings.API_KEY)
    schedule.every().day.at(settings.AUTO_QUESTION_TIME).do(
        enviar_questao_automatica(updater.bot))

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", Start()))
    dp.add_handler(CommandHandler("help", Help()))
    dp.add_handler(CommandHandler("perguntar", AskQuestion()))
    dp.add_handler(CommandHandler("estatisticas", Statistics()))
    dp.add_handler(CommandHandler("limpar_dados", ClearData()))
    dp.add_handler(CommandHandler("ativar_questao_automatica", EnableAutoQuestion()))
    dp.add_handler(CommandHandler("desativar_questao_automatica", DisableAutoQuestion()))
    dp.add_handler(CallbackQueryHandler(QueryHandler()))
    dp.add_error_handler(error)
    updater.start_polling()
    thread = threading.Thread(target=task_runner)
    thread.daemon = True
    thread.start()
    updater.idle()


if __name__ == '__main__':
    main()
