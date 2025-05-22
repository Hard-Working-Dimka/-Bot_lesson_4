from enum import Enum
import telegram
from environs import env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from file_processing import get_question
from redis_connection import connect_to_db

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
        fr'Hi {user.mention_markdown_v2()}\!', reply_markup=reply_markup,
    )
    return Handlers.QUESTION


def handle_give_up(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=f'Очень жаль что ты сдался :(( Правильный ответ: "{context.user_data['right_answer']}"',
        reply_markup=reply_markup)
    update.message.reply_text(
        text='Новый вопрос')
    return Handlers.QUESTION


def handle_solution_attempt(update: Update, context: CallbackContext):
    answer = update.message.text
    if context.user_data['right_answer'].split('.', 1)[0] == answer or \
            context.user_data['right_answer'].split(' (', 1)[0] == answer:
        update.message.reply_text(text='Ответ верный!', reply_markup=reply_markup)
    else:
        update.message.reply_text(text=f'Ты профукал! Правильный ответ: "{context.user_data['right_answer']}"',
                                  reply_markup=reply_markup)

    return Handlers.QUESTION


def handle_new_question_request(update: Update, context: CallbackContext):
    question = get_question()
    update.message.reply_text(text=question[0], reply_markup=reply_markup)
    context.user_data['right_answer'] = question[1]
    print(question[1])
    print('________________________________')
    print(question)
    return Handlers.RESULT


# def send_question(update: Update, context: CallbackContext, reply_markup, db) -> None:
#     user_id = update.effective_user.id
#     message = update.message.text
#     if message == 'Новый вопрос':
#         question = get_question()
#         db.set(user_id, question[0])
#         print(db.get(user_id))
#         update.message.reply_text(text=question[0], reply_markup=reply_markup)


def main():
    db = connect_to_db()

    env.read_env()
    tg_bot = Updater(env('TG_TOKEN'))

    dispatcher = tg_bot.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            Handlers.QUESTION: [MessageHandler(Filters.regex('^(Новый вопрос)$'),
                                               handle_new_question_request, ),
                                ],

            Handlers.RESULT: [MessageHandler(Filters.text,
                                             handle_solution_attempt,
                                             pass_user_data=True),
                              ],

            Handlers.RIGHT_ANSWER: [MessageHandler(Filters.regex('^(Сдаться)$'),
                                                   handle_give_up),
                                    ],
        },

        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    tg_bot.start_polling()

    tg_bot.idle()


if __name__ == '__main__':
    main()
