from commands.command_handler import CommandHandler
from template_helper import render


class Statistics(CommandHandler):

    def handle(self):
        respondidas = len(self.user.respondidas)
        acertos = len(self.user.acertos)
        erros = len(self.user.erros)

        context = {
            'respondidas': respondidas,
            'acertos': acertos,
            'acertos_porcent': acertos * 100. / max(respondidas, 1),
            'erros': erros,
            'erros_porcent': erros * 100. / max(respondidas, 1)
        }

        reply = render('estatisticas.tpl', **context)
        self.reply_text(reply, parse_mode='html')
