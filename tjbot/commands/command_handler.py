from models import User


class CommandHandler(object):

    def __call__(self, bot, update):
        self.bot = bot
        self.update = update
        self.user = User.objects.get(telegram_id=update.message.from_user.id)
        try:
            self.handle()
        except Exception as e:
            print 'Error while processing command:', e
            self.reply_error()

    def handle(self):
        raise NotImplementedError('You must implement handle method')

    def reply_text(self, text):
        self.update.message.reply_text(text)

    def reply_error(self):
        self.reply_text('Erro ao processar comando, tente novamente')
