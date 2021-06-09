import discord
from discord.ext import commands
from utils import Gunibot, MyContext


class Quizz(commands.Cog):

    def __init__(self, bot: Gunibot):
        self.bot = bot
        self.file = ""

    def get_question(self, question_id):
        payload = self.bot.db_query("SELECT * FROM quizz WHERE id = ?", (question_id,))
        for question in payload: return question

    def add_question(self, user_question, user_awnser):
        self.bot.db_query("INSERT INTO quizz (question, awnser) VALUES(?, ?)", (user_question, user_awnser))

    def delete_question(self, question_id):
        self.bot.db_query("DELETE FROM quizz WHERE id = ?", (question_id, ))


def setup(bot):
    bot.add_cog(Quizz(bot))
