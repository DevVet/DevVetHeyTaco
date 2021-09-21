from datetime import datetime
import discord
from pg2db import has_given_today, add_transaction, get_this_months_scores, init_db_conn

BOT_IDS = [785953175865524244,773282415548039228, 730885117656039466, 616754792965865495]
JSONID = 542354928300195851
conn = init_db_conn()

async def deny(reason, message, sender_given):
    response = ''
    if reason == "selfTaco": 
        response = "You cant't give yoruself tacos, dumbass"
    elif reason == "notEnough":
        response = f"You can only give 5 tacos a day, \
                and you have already given {sender_given}"
    
    await message.channel.send(f"<@{message.author.id}>, {response}")


async def handle_taco(message):
    recipients = list(filter(lambda r: r not in BOT_IDS, message.raw_mentions))
    sender = message.author.id
    sender_given = has_given_today(conn, sender)
    sender_has_enough_tacos = len(recipients) <= (5 - sender_given)

    if len(recipients) < 1:
            return
    if sender in recipients:
        await deny("selfTaco", message)
    elif sender == JSONID or JSONID in recipients:
        await message.channel.send("Fuck you json")
    elif sender_has_enough_tacos:
        recipients_strs = []
        for recipient in recipients:
            add_transaction(conn, sender, recipient)
            recipients_strs.append(f"<@{recipient}>" )
        
        await message.channel.send(
            f"<@{sender}> gave tacos to {' '.join(recipients_strs)}"
        )
    else:
        await deny("notEnough", message, sender_given)

async def getEmbed(data, guild):
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
        guild_member_name = await guild.fetch_member(taco[0])
        embed.add_field(
            name=guild_member_name.display_name,
            value=taco[1],
            inline=True
        )
    return embed

async def handle_taco_scores(ctx):
    data = get_this_months_scores(conn)
    embed = await getEmbed(data, ctx.channel.guild)
    await ctx.channel.send(embed=embed)