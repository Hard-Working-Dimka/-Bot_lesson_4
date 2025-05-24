from enum import Enum
import telegram
from environs import env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from file_processing import get_question

keyboard = [['Новый вопрос', 'Сдаться'],
            ['Мой счет']]
reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


class Handlers(Enum):
    RIGHT_ANSWER = 'handle_give_up'
    RESULT = 'handle_solution_attempt'
    QUESTION = 'handle_new_question_request'


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! \n\n Для продолжения нажми кнопку "Новый вопрос"',
        reply_markup=reply_markup,
    )
    return Handlers.QUESTION


def handle_give_up(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=f'Очень жаль что ты сдался. Правильный ответ: {context.user_data['right_answer']} \n\n Для продолжения нажми кнопку "Новый вопрос"',
        reply_markup=reply_markup)
    return Handlers.QUESTION


def handle_solution_attempt(update: Update, context: CallbackContext):
    answer = update.message.text
    if context.user_data['right_answer'].split('.', 1)[0] == answer or \
            context.user_data['right_answer'].split(' (', 1)[0] == answer:
        update.message.reply_text(text='Ответ верный! \n\n Для продолжения нажми кнопку "Новый вопрос"',
                                  reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text=f'Ты проиграл! Правильный ответ: "{context.user_data['right_answer']}" \n\n Для продолжения нажми кнопку "Новый вопрос"',
            reply_markup=reply_markup)

    return Handlers.QUESTION


def handle_new_question_request(update: Update, context: CallbackContext, path_to_questions):
    question = get_question(path_to_questions)
    update.message.reply_text(text=question[0], reply_markup=reply_markup)
    context.user_data['right_answer'] = question[1]
    return Handlers.RESULT


def main():
    env.read_env()
    tg_bot = Updater(env('TG_TOKEN'))

    dispatcher = tg_bot.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            Handlers.QUESTION: [
                MessageHandler(Filters.regex('^(Новый вопрос)$'),
                               lambda update, context: handle_new_question_request(update, context,
                                                                                   env.str('PATH_TO_QUESTIONS'))),
            ],

            Handlers.RESULT: [MessageHandler(Filters.regex('^(Сдаться)$'),
                                             handle_give_up),
                              MessageHandler(Filters.text,
                                             handle_solution_attempt,
                                             pass_user_data=True),

                              ],
        },

        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    tg_bot.start_polling()

    tg_bot.idle()


if __name__ == '__main__':
    main()
