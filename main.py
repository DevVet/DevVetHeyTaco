import os
from datetime import datetime

import discord
from discord_slash import SlashCommand
from dotenv import load_dotenv

from pg2db import init_db_conn, has_given_today, add_transaction, get_this_months_scores

MONTH = [
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

HEY_TACO_BOT_ID = '785953175865524244'


class MyClient(discord.Client):
    async def on_ready(self):
        self.conn = init_db_conn()
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if "🌮" in message.content:
            sender = message.author.id
            recipients = message.raw_mentions
            sender_given = has_given_today(self.conn, sender)
            if len(recipients) < 1:
                    return
            if sender in recipients:
                await message.channel.send(
                    f"<@{sender}>, You cant give yourself a taco"
                )
            elif HEY_TACO_BOT_ID in recipients:
                await message.channel.send(
                    f"<@{sender}>, I DONT NEED YO TACOS! I GOT THE TACOS!!!!"
                )
            elif (5 - sender_given) >= len(recipients):
                for recipient in recipients:
                    add_transaction(self.conn, sender, recipient)
                recipients_strs = [
                    f"<@{recipient}>" for recipient in recipients
                ]
                await message.channel.send(
                    f"<@{sender}> gave tacos to {' '.join(recipients_strs)}"
                )
            else:
                await message.channel.send(
                    f"<@{sender}>, You can only give 5 tacos a day, \
                        and you have already given {sender_given}"
                )

        elif "!tacoscores" in message.content:
            data = get_this_months_scores(self.conn)
            now = datetime.now()
            embed = discord.Embed(
                title=f"Scores for {MONTH[now.month - 1]} {now.year}",
                description=f"A total of {sum([taco[1] for taco in data])} \
                    have been given this month"
            )
            for taco in data:
                guild_member_name = await message.channel.guild.fetch_member(taco[0])
                embed.add_field(
                    name=guild_member_name.display_name,
                    value=taco[1],
                    inline=False
                )

            await message.channel.send(embed=embed)


client = MyClient(intents=discord.Intents.all())
slash = SlashCommand(client, auto_register=True)

DEVVET_GUILD_ID = 765949464443617331
guild_ids = [DEVVET_GUILD_ID]


@slash.slash(
    name="tacoscores",
    description="Returns this month's taco scores",
    guild_ids=guild_ids
)
async def _send_taco_scores(ctx):
    data = get_this_months_scores(init_db_conn())

    now = datetime.now()

    if len(data) > 0:
        await ctx.channel.send(
            f"***Scores for{MONTH[now.month - 1]} {now.year}***.\nA total of {sum([taco[1] for taco in data])} have "
            f"been given this month "
        )

        for taco in data:
            guild_member = await ctx.channel.guild.fetch_member(taco[0])
            embed = discord.Embed(title=taco[1])
            embed.set_author(
                name=guild_member.display_name,
                icon_url=guild_member.avatar_url
            )
            await ctx.channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title="No tacos awarded this month",
            description="Go get some Tacos!"
        )
        await ctx.channel.send(embed=embed)


if __name__ == "__main__":
    load_dotenv()

    client.run(os.getenv("DISCORD_KEY"))
