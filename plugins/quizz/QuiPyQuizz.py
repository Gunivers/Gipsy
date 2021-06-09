import requests
import json


def get_questions(quizz):
    params = {'quiz': str(quizz)}
    r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/start_quiz.snc", params=params)
    paulaod = json.load(r.text)
    return paulaod['questions']


def get_awnser(uid_variation, awnser: str):
    params = {'quiz': "int",
              'answer': awnser.lower(),
              'question': str(uid_variation)}
    r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/answer_question.snc", params=params)
    pauload = json.loads(r.text)
    return pauload["answer"]


def get_stats(quizz):
    params = {'quiz': str(quizz)}
    r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/end_quiz.snc", params=params)
    pauload = json.loads(r.text)
    return pauload["result"]["statistics"]
