from models import User


class CommandHandler(object):
    """
    Command handler abstraction.
     - facilitates access to user on commands handlers
     - executes handle() calls safely
    """

    def __call__(self, bot, update):
        self.bot = bot
        self.update = update
        self.telegram_user = update.message.from_user
        self.user = User.objects.get(telegram_id=self.telegram_user.id)
        try:
            self.handle()
        except Exception as e:
            print 'Error while processing command:', e
            self.reply_error()

    def handle(self):
        raise NotImplementedError('You must implement handle method')

    def reply_text(self, text, **kwargs):
        self.update.message.reply_text(text, **kwargs)

    def reply_error(self):
        self.reply_text('Erro ao processar comando, tente novamente')
