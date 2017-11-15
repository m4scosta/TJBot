# coding: utf-8
from commands.command_handler import CommandHandler


class EnableAutoQuestion(CommandHandler):

    def handle(self):
        if not self.user.questao_automatica_ativa:
            self.user.questao_automatica_ativa = True
            self.user.save()
        self.reply_text('Questão automática ativada com sucesso.')


class DisableAutoQuestion(CommandHandler):

    def handle(self):
        if self.user.questao_automatica_ativa:
            self.user.questao_automatica_ativa = False
            self.user.save()
            reply = 'Questão automática desativada com sucesso.'
        else:
            reply = 'Questão automática não está ativa, nada feito.'
        self.reply_text(reply)
