from dotenv import load_dotenv
import os
import discord
import datetime
from db import *

load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        self.conn = init_db_conn()
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if "🌮" in message.content:
            sender = message.author.id
            recipients = message.raw_mentions
            sender_given = has_given_today(self.conn, sender)
            if sender in recipients:
                await message.channel.send(f"<@{sender}>, You cant give yourself a taco")
            elif sender_given < len(recipients):
                for recipient in recipients:
                    add_transaction(self.conn, sender, recipient)
                    recipients = [f"<@{recipient}>" for recipient in recipients]
                await message.channel.send(f"<@{sender}> gave tacos to {' '.join(recipients)}")
            else:
                await message.channel.send(f"<@{sender}>, You can only give 5 tacos a day, and you have already given {sender_given}")

        elif "!tacoscores" in message.content:
            data = get_this_months_scores(self.conn)
            data = [f"<@{taco[0]}> - {taco[1]}" for taco in data]
            out_message = '\n'.join(data)
            print(out_message)
            message.channel.send(out_message)

client = MyClient()
client.run(os.getenv("DISCORD_KEY"))

