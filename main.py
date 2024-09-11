# discordpy imports
import discord
from discord.ext import commands
from discord import app_commands

# standard imports
import json
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# custom import
import style as style

logging.basicConfig(level=logging.INFO, format=style.logging_format)

STAR_CHOICES = [
    app_commands.Choice(name="⭐", value=1),
    app_commands.Choice(name="⭐⭐", value=2),
    app_commands.Choice(name="⭐⭐⭐", value=3),
    app_commands.Choice(name="⭐⭐⭐⭐", value=4),
    app_commands.Choice(name="⭐⭐⭐⭐⭐", value=5),
]

env_vars = None  # both placesholders
FILE_PATH = None

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!!!", intents=intents, activity=discord.Activity(type=discord.ActivityType(3), name="Test"))

def write_json(data: dict) -> str:
    try:
        with open(FILE_PATH, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return e

def load_json() -> tuple[dict, str]:
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r', encoding="utf8") as file:
                return json.load(file), ""
        except json.JSONDecodeError as e:
            return {}, e
    else:
        return {}, None


def get_embed(star_string: str, message: str, new_vouch_nr: int, user: discord.User, image: discord.Attachment) -> discord.Embed:
    now = datetime.now()
    embed = discord.Embed(title=style.vouch_title_text, description=star_string, colour=style.color, timestamp=now)
    embed.add_field(name=style.vouch_message_text, value=message, inline=False)
    embed.add_field(name=style.vouch_nr_text, value=new_vouch_nr, inline=True)
    embed.add_field(name=style.vouch_by_text, value=f"{user.mention}", inline=True)
    embed.set_thumbnail(url=user.display_avatar)
    embed.set_footer(text=client.user.name, icon_url=env_vars['icon_url'])
    embed.set_image(url=image.url)

    return embed

@client.event
async def on_ready():
    await client.tree.sync(guild=discord.Object(id=env_vars['guild_id']))  
    logging.info("Connected to Discord.")

    
def load_env_vars():
    logging.info("Loading environment variables.")
    load_dotenv()
    try:
        return {
            "guild_id": int(os.getenv("GUILD_ID")),
            "discord_token": os.getenv("DISCORD_AUTH_TOKEN"),
            "channel_id": int(os.getenv("CHANNEL_ID")),
            "command_prefix": os.getenv("COMMAND_PREFIX"),
            "activity_text": os.getenv("ACTIVITY_TEXT"),
            "icon_url": os.getenv("ICON_URL"),
            "path_to_json": os.getenv("PATH_TO_JSON"),
        }
    except (TypeError, ValueError):
        logging.error("Failed to load environment variables.")
        raise

def set_file_path(path_to_json):
    return os.path.join(os.curdir, path_to_json)

    
def register_commands():
    @client.tree.command(name=style.command_name_text, description=style.command_description_text, guild=discord.Object(id=env_vars['guild_id']))
    @app_commands.describe(stars=style.command_stars_description_text, message=style.command_message_description_text, image=style.command_image_description_text)
    @app_commands.choices(stars=STAR_CHOICES)
    async def vouch(ctx: discord.Interaction, stars: app_commands.Choice[int], message: str, image: discord.Attachment):
        await ctx.response.defer(thinking=True)
        
        logging.info(f"Command {style.command_name_text} invoked by {ctx.user.name}")

        if ctx.channel_id != env_vars['channel_id']:
            logging.warning(f"Command invoked in wrong channel: {ctx.channel.name}")
            await ctx.followup.send(style.wrong_channel_error_text)
            return

        # load data
        data, load_error = load_json()
        if load_error:
            logging.error(f"Error while loading {env_vars['path_to_json']}: {load_error}")
            await ctx.followup.send(style.json_error_text, ephemeral=True)
            return

        # if no data ..
        if data:
            new_vouch_nr = int(max(data.keys())) + 1
        else:
            new_vouch_nr = 1

        star_string = "⭐" * stars.value
        now = datetime.now()

        # validate images
        if image is None or not image.content_type.startswith('image/'):
            logging.error("Something went wrong with the image.")
            await ctx.followup.send(style.image_error_text, ephemeral=True)
            return

        embed = get_embed(star_string, message, new_vouch_nr, ctx.user, image)

        # add new entry
        data[new_vouch_nr] = {
            "date": now.strftime(style.date_format),
            "message": message,
            "user": ctx.user.id,
            "stars": stars.value
        }

        # write data
        write_error = write_json(data)
        if write_error:
            logging.error(f"Error while saving {env_vars['path_to_json']}: {write_error}")
            await ctx.followup.send(style.json_error_text, ephemeral=True)
            return

        # change channel name to account for new_vouch
        await ctx.channel.edit(name=style.vouch_channel_name.format(new_vouch_nr))
        
        # sendit
        await ctx.followup.send(embed=embed)
        
        logging.info(f"Successfully saved vouch {new_vouch_nr}.")
    
    
def run():
    global env_vars, FILE_PATH
    env_vars = load_env_vars()  # Load environment variables at runtime
    FILE_PATH = set_file_path(env_vars["path_to_json"])  # Set the file path
    register_commands()  # Register the commands
    client.run(env_vars["discord_token"])

if __name__ == "__main__":
    run()
