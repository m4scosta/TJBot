from commands.command_handler import CommandHandler
from template_helper import render


class Help(CommandHandler):

    def handle(self):
        self.reply_text(render('help.tpl', user=self.telegram_user))
