import os

import discord
from discord_slash import SlashCommand
from dotenv import load_dotenv

from ops import handle_taco, handle_taco_scores


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if "🌮" in message.content:
           handle_taco(message) 

        elif "!tacoscores" in message.content:
           handle_taco_scores(message) 


# Setup slash commands
client = MyClient(intents=discord.Intents.all())
slash = SlashCommand(client, auto_register=True)
DEVVET_GUILD_IDS = [765949464443617331]

@slash.slash(
    name="tacoscores",
    description="Returns this month's taco scores",
    guild_ids=DEVVET_GUILD_IDS
)
async def _send_taco_scores(ctx):
    handle_taco_scores(ctx)


if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("DISCORD_KEY"))
