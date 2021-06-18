import requests
import json

with open('data.json', 'r', encoding='utf-8') as f: data = json.load(f.read())


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


def get_name(uid_variation):
    if uid_variation in data: return data[uid_variation]['name']
    else: return None


def get_url(uid_variation):
    if uid_variation in data: return  data[uid_variation]['url']
    else: return None
