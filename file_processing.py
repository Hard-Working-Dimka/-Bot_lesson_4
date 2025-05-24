import random


def get_question(path_to_questions):
    with open(path_to_questions, "r", encoding='KOI8-R') as file:
        questions = file.read()

    question_blocks = questions.split('\n\n\n')
    questions = {}

    for question_block in question_blocks:
        question_block = question_block.strip().split('\n\n')
        for question in question_block:
            if question.startswith('Вопрос'):
                question_name = question.split('\n', maxsplit=1)[1].replace('\n', ' ').strip()
            if question.startswith('Ответ'):
                question_answer = question.split('\n', maxsplit=1)[1].replace('\n', ' ').strip()
        questions[question_name] = question_answer

    return random.choice(list(questions.items()))
