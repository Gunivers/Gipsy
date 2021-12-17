import sqlite3

def add_topic(self, guild, title, description, emoji):
    try:
        query = "INSERT INTO contact_topics (guild,title,description,emoji) VALUES (?, ?, ?, ?)"
        self.bot.db_query(query, (guild, title, description, emoji))
    except sqlite3.OperationalError as e:
        print(e)

async def list_topic(self, ctx, guild):
    for topic in get_topics(self, guild):
        await ctx.send("{}__**{}**__\n{}\n".format(topic[0],topic[1],topic[2]))

def remove_topic(guild, topic):
    pass

def get_topics(self, guild):
    query = 'SELECT * FROM contact_topics WHERE guild=?'
    return self.bot.db_query(query, (guild))
