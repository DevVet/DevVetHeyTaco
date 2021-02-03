from dotenv import load_dotenv
import os
import discord
import datetime
from pg2db import *

load_dotenv()
MONTH= [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
    ]

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
            elif '785953175865524244' in recipients:
                await message.channel.send(f"<@{sender}>, I DONT NEED YO TACOS! I GOT THE TACOS!!!!")
            elif (5 - sender_given) >= len(recipients):
                for recipient in recipients:
                    add_transaction(self.conn, sender, recipient)
                recipients_strs = [f"<@{recipient}>" for recipient in recipients]
                await message.channel.send(f"<@{sender}> gave tacos to {' '.join(recipients_strs)}")
            else:
                await message.channel.send(f"<@{sender}>, You can only give 5 tacos a day, and you have already given {sender_given}")

        elif "!tacoscores" in message.content:
            data = get_this_months_scores(self.conn)
            data = await [(message.channel.guild.fetch_member(taco[0]).nick, taco[1]) for taco in data]
            now = datetime.now()
            embed = discord.Embed(title=f"Scores for {MONTH[now.month - 1]} {now.year}", description=f"A total of {sum([taco[1] for taco in data])} have been given this month")
            for taco in data:
                embed.add_field(name=taco[0], value=taco[1], inline=False)
            
            await message.channel.send(embed=embed)

client = MyClient()
client.run(os.getenv("DISCORD_KEY"))

