from commands.command_handler import CommandHandler


class ClearData(CommandHandler):

    SUCCESS_MSG = 'Dados apagados com sucesso'

    def handle(self):
        self.user.update(respondidas=[], erros=[], acertos=[])
        self.reply_text(self.SUCCESS_MSG)
