import requests
import json
import os


class QuiPyQuizz:
    def __init__(self):
        try:
            with open(f'{os.getcwd()}\plugins\quizz\data.json', 'r', encoding='utf-8') as f: self.data = json.load(f)
        except FileNotFoundError:
            with open(f'{os.getcwd()}\data.json', 'r', encoding='utf-8') as f: self.data = json.load(f)

    @staticmethod
    def request_questions(quizz):
        params = {'quiz': str(quizz)}
        r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/start_quiz.snc", params=params)
        paulaod = json.loads(r.text)
        return paulaod['questions']

    @staticmethod
    def request_awnser(uid_variation, question_id, awnser: str):
        params = {'quiz': uid_variation,
                  'answer': awnser.lower(),
                  'question': question_id}
        r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/answer_question.snc", params=params)
        pauload = json.loads(r.text)
        return pauload["answer"]

    @staticmethod
    def request_stats(quizz):
        params = {'quiz': str(quizz)}
        r = requests.get(url="https://quipoquiz.com/module/sed/quiz/fr/end_quiz.snc", params=params)
        pauload = json.loads(r.text)
        return pauload["result"]["statistics"]

    def get_name(self, uid_variation):
        if uid_variation in self.data: return self.data[uid_variation]['name']
        else: return None

    def get_url(self, uid_variation):
        if uid_variation in self.data: return f"https://quipoquiz.com/quiz/{self.data[uid_variation]['url']}"
        else: return None

    def get_question(self, uid_variation, question_id):
        if uid_variation in self.data and question_id in self.data[uid_variation]['questions']:
            return self.data[uid_variation]['questions'][question_id]
        else: return None

    def get_awnser(self, uid_variation, question_id):
        if uid_variation in self.data and question_id in self.data[uid_variation]['awnsers']:
            return self.data[uid_variation]['awnsers'][question_id]
        else: return None
