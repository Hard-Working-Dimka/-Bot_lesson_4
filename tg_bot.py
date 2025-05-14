import telegram
from environs import env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from file_processing import get_question


def start(update: Update, context: CallbackContext, reply_markup) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!', reply_markup=reply_markup,
    )


def send_question(update: Update, context: CallbackContext, reply_markup) -> None:
    message = update.message.text
    if message == 'Новый вопрос':
        question = get_question()

        update.message.reply_text(text=question[0], reply_markup=reply_markup)
    if message == 'Сдаться':
        update.message.reply_text(text='это меню сдаться', reply_markup=reply_markup)
    if message == 'Мой счет':
        update.message.reply_text(text='Это меню моего счета', reply_markup=reply_markup)


def main() -> None:
    keyboard = [['Новый вопрос', 'Сдаться'],
                ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard)

    env.read_env()
    tg_bot = Updater(env('TG_TOKEN'))

    dispatcher = tg_bot.dispatcher

    dispatcher.add_handler(CommandHandler("start", lambda update, context: start(update, context,
                                                                                 reply_markup)))

    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, lambda update, context: send_question(update, context,
                                                                                              reply_markup)))

    tg_bot.start_polling()

    tg_bot.idle()


if __name__ == '__main__':
    main()
