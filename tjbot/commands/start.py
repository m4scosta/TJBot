from template_helper import render
from models import User


class Start(object):
    """
    Handles /start command setting up user on database
    """

    def __call__(self, bot, update):
        user = update.message.from_user
        chat_id = update.message.chat.id

        if not User.objects(telegram_id=user.id):
            User(telegram_id=user.id, chat_id=chat_id).save()
        else:
            User(chat_id=chat_id)

        update.message.reply_text(render('start.tpl', user=user.first_name))
