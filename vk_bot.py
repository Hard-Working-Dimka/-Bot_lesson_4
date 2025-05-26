import random
from file_processing import get_questions
from redis_connection import connect_to_db

import vk_api as vk
from environs import env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


def give_up(event, vk_api, keyboard, db):
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Очень жаль что ты сдался. Правильный ответ: "{db.get(event.user_id)}" \n\n Для продолжения нажми кнопку "Новый вопрос"',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def check_answer(event, vk_api, keyboard, db):
    answer = db.get(event.user_id)

    if answer.split('.', 1)[0] == event.text or \
            answer.split(' (', 1)[0] == event.text:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Ответ верный! \n\n Для продолжения нажми кнопку "Новый вопрос"',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message=f'Ты проиграл! Правильный ответ: "{answer}" \n\n Для продолжения нажми кнопку "Новый вопрос"',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )


def get_new_question(event, vk_api, keyboard, db, questions):
    question = random.choice(list(questions.items()))
    db.set(event.user_id, question[1])
    vk_api.messages.send(
        user_id=event.user_id,
        message=question[0],
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


if __name__ == "__main__":
    env.read_env()

    vk_session = vk.VkApi(token=env('VK_API_KEY'))

    questions = get_questions(env.str('PATH_TO_QUESTIONS'))

    host = env.str('HOST')
    port = env.int('PORT')
    password = env.str('PASSWORD')
    db = connect_to_db(host=host, port=port, password=password)

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет')

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue
        if event.text == "Сдаться":
            give_up(event, vk_api, keyboard, db)
        elif event.text == "Новый вопрос":
            get_new_question(event, vk_api, keyboard, db, questions)
        elif event.text == "Мой счет":
            pass
        elif event.text == "/start":
            pass
        else:
            check_answer(event, vk_api, keyboard, db)
