from datetime import datetime
import discord
from pg2db import has_given_today, add_transaction, get_this_months_scores, init_db_conn

HEY_TACO_BOT_ID = '785953175865524244'
conn = init_db_conn()

def deny(reason, message):
    response = ''
    if reason == "selfTaco": 
        response = "You cant't give yoruself tacos, dumbass"
    elif reason == "notEnough":
        response = "You dont have enough tacos for that"
    elif reason == "botTaco":
        response = "I dont need your stinkin' tacos... I HAVE ALL THE TACOS!!!"
    
    message.channel.send(f"<@{message.sender}>, {response}")


def handle_taco(message):
    recipients = message.raw_mentions
    sender = message.author.id
    sender_given = has_given_today(conn, sender)
    sender_has_enough_tacos = len(recipients) <= (5 - sender_given)
    
    if len(recipients) < 1:
            return
    if sender in recipients:
        deny("selfTaco", message)
    elif HEY_TACO_BOT_ID in recipients:
        deny("botTaco", message)
    elif sender_has_enough_tacos:
        recipients_strs = []
        for recipient in recipients:
            add_transaction(conn, sender, recipient)
            recipients_strs.append(f"<@{recipient}>" )
        
        message.channel.send(
            f"<@{sender}> gave tacos to {' '.join(recipients_strs)}"
        )
    else:
        message.channel.send(
            f"<@{sender}>, You can only give 5 tacos a day, \
                and you have already given {sender_given}"
        )

async def getEmbed(data, fetch_member):
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
    now = datetime.now()
    embed = discord.Embed(
        title=f"Scores for {MONTH[now.month - 1]} {now.year}",
        description=f"A total of {sum([taco[1] for taco in data])} \
            have been given this month"
    )
    for taco in data:
        guild_member_name = await fetch_member(taco[0])
        embed.add_field(
            name=guild_member_name.display_name,
            value=taco[1],
            inline=True
        )

async def handle_taco_scores(ctx):
    data = get_this_months_scores(conn)
    embed = getEmbed(data, ctx.channel.guild.fetch_member)
    await ctx.channel.send(embed=embed)