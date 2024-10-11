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

# both placesholders
env_vars = None
FILE_PATH = None

class VERIFY(discord.ui.View):
    def __init__(self, verify_url):
        super().__init__()
        button = discord.ui.Button(label='Please verify here!', style=discord.ButtonStyle.blurple, url=verify_url)
        self.add_item(button)

intents = discord.Intents.default()
client = commands.Bot(command_prefix=style.command_prefix_text, intents=intents)

def write_json(data: dict, file_path) -> str:
    """writing to a json-file

    Args:
        data (dict): data that gets written back

    Returns:
        str: Exception as str (optional)
    """
    try:
        with open(file_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return e

def load_json(file_path) -> tuple[dict, str]:
    """loading a json file into a dict

    Returns:
        tuple[dict, str]: dictionary, Exception as str
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding="utf8") as file:
                return json.load(file), None
        except json.JSONDecodeError as e:
            return {}, e
    else:
        return {}, None
 
def load_env_vars() -> dict:
    """loading the env_vars from the .env

    Returns:
        dict: env_vars as dict
    """
    logging.info("Loading environment variables.")
    load_dotenv()
    try:
        return {
            "guild_id": int(os.getenv("GUILD_ID")),
            "discord_token": os.getenv("DISCORD_AUTH_TOKEN"),
            "channel_id": int(os.getenv("CHANNEL_ID")),
            "activity_text": os.getenv("ACTIVITY_TEXT"),
            "icon_url": os.getenv("ICON_URL"),
            "path_to_json": os.getenv("PATH_TO_JSON"),
            "verify_url": os.getenv("VERIFY_URL"),
            "verify_backup_image": os.getenv('VERIFY_BACKUP_IMAGE')
        }
    except (TypeError, ValueError):
        logging.error("Failed to load environment variables.")
        raise

def get_embed(star_string: str, message: str, product: str, new_vouch_nr: int, user: discord.User, image: discord.Attachment) -> discord.Embed:
    """returns the embed that will be sent after a vouch has been received

    Args:
        star_string (str): star emojis concatinated as a string
        message (str): user_message
        new_vouch_nr (int): new_vouch_nr 
        user (discord.User): user that invoked the command
        image (discord.Attachment): user screenshot

    Returns:
        discord.Embed: embed that gets returned
    """
    now = datetime.now()
    embed = discord.Embed(title=style.vouch_title_text, description=star_string, colour=style.color, timestamp=now)
    embed.add_field(name=style.vouch_message_text, value=message, inline=False)
    embed.add_field(name=style.vouch_nr_text, value=new_vouch_nr, inline=True)
    embed.add_field(name=style.vouch_by_text, value=f"{user.mention}", inline=True)
    embed.add_field(name=style.vouch_product, value=product, inline=True)
    embed.set_thumbnail(url=user.display_avatar)
    embed.set_footer(text=client.user.name, icon_url=env_vars['icon_url'])
    embed.set_image(url=image.url)

    return embed

def get_verify_embed():
    now = datetime.now()
    embed = discord.Embed(title=style.verify_embed_title,
                      description=style.verify_embed_description,
                      colour=style.color, timestamp=now)

    embed.set_author(name=client.user.name)
    embed.set_image(url=env_vars['verify_backup_image'])
    embed.set_footer(text=client.user.name, icon_url=env_vars['icon_url'])
    return embed

def get_guess_embed(start: int, end: int, price):
    now = datetime.now()
    embed = discord.Embed(title=style.guess_embed_title,
                      description=style.guess_embed_description,
                      colour=style.color, timestamp=now)

    embed.set_author(name=client.user.name)
    embed.add_field(name="Numbers",
                value=f"Guess between **{start}** and **{end}**!",
                inline=True)
    embed.add_field(name="Price",
                value=f"**{price}**",
                inline=True)
    embed.set_footer(text=client.user.name, icon_url=env_vars['icon_url'])
    return embed

def get_winner_embed(user, price, actual_number):
    now = datetime.now()
    embed = discord.Embed(title=style.guess_winner_embed_title,
                      description=style.guess_winner_embed_description.format(user, price, actual_number),
                      colour=style.color, timestamp=now)

    embed.set_author(name=client.user.name)
    embed.set_footer(text=client.user.name, icon_url=env_vars['icon_url'])#
    return embed

async def handle_guess_end(ctx: discord.Interaction) -> None:
    """Handles the logic for ending the guessing competition."""
    try:
        os.remove(style.guess_path)
    except Exception as exc:
        await ctx.followup.send(style.guess_error_text.format(exc), ephemeral=True)
        return
    
    if not ctx.user.guild_permissions.administrator:
        return
    
    await ctx.followup.send(style.guess_end_text, ephemeral=True)

@client.event
async def on_ready() -> None:
    """whenever the bot is ready..
    """
    await client.tree.sync(guild=discord.Object(id=env_vars['guild_id']))  
    logging.info("Connected to Discord.")
    
def register_commands() -> None:
    """command gets called to add commands to bot, used this way because of auto-unit-tests, but looks crappy.
    """
    
    # Vouch Command

    @client.tree.command(name=style.command_name_text, description=style.command_description_text, guild=discord.Object(id=env_vars['guild_id']))
    @app_commands.describe(stars=style.command_stars_description_text, message=style.command_message_description_text, product=style.command_product_description_text, image=style.command_image_description_text)
    @app_commands.choices(stars=STAR_CHOICES)
    async def vouch(ctx: discord.Interaction, stars: app_commands.Choice[int], message: str, product: str, image: discord.Attachment) -> None:
        """vouch_command

        Args:
            ctx (discord.Interaction): context of command invocation
            stars (app_commands.Choice[int]): option picked by user
            message (str): message delivered by user
            image (discord.Attachment): screenshot of user
        """
        await ctx.response.defer(thinking=True)
        
        logging.info(f"Command {style.command_name_text} invoked by {ctx.user.name}")

        if ctx.channel_id != env_vars['channel_id']:
            logging.warning(f"Command invoked in wrong channel: {ctx.channel.name}")
            await ctx.followup.send(style.wrong_channel_error_text)
            return

        # load data
        data, load_error = load_json(FILE_PATH)
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

        embed = get_embed(star_string, message, product, new_vouch_nr, ctx.user, image)

        # add new entry
        data[new_vouch_nr] = {
            "date": now.strftime(style.date_format),
            "message": message,
            "product": product,
            "user": ctx.user.id,
            "stars": stars.value
        }

        # write data
        write_error = write_json(data, FILE_PATH)
        if write_error:
            logging.error(f"Error while saving {env_vars['path_to_json']}: {write_error}")
            await ctx.followup.send(style.json_error_text, ephemeral=True)
            return

        # change channel name to account for new_vouch
        await ctx.channel.edit(name=style.vouch_channel_name.format(new_vouch_nr))
        
        # sendit
        message: discord.WebhookMessage = await ctx.followup.send(embed=embed, wait=True)
        
        await message.add_reaction("<a:azulcoroainf24:1252338853835182210>")
        
        logging.info(f"Successfully saved vouch {new_vouch_nr}.")
    
    @client.tree.command(name=style.command_verify_name_text, description=style.command_verify_description_text, guild=discord.Object(id=env_vars['guild_id']))
    async def verify_embed(ctx: discord.Interaction) -> None:

        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(style.admin_error_text, ephemeral=True)
            return

        # Defer the response (shows bot is thinking)
        await ctx.response.defer()

        # Create the embed that will be sent
        embed = get_verify_embed()

        # Send the embed along with the view (which contains the button)
        await ctx.followup.send(embed=embed, view=VERIFY(env_vars['verify_url']))

    @client.tree.command(name=style.command_guess_create_name_text, description=style.command_guess_create_description_text, guild=discord.Object(id=env_vars['guild_id']))
    async def guess_create(ctx: discord.Interaction, start: int, end: int, actual_number: int, price: str):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(style.admin_error_text, ephemeral=True)
            return

        # Defer the response (shows bot is thinking)
        await ctx.response.defer()
        
        # If a guess is currently active, end it before
        if os.path.isfile(style.guess_path):
            await ctx.followup.send(style.guess_create_still_active_text, ephemeral=True)
            return
        
        data = {
            "winner_number": actual_number,
            "start": start,
            "end": end,
            "price": price,
            "participants": 0
        }
        
        # Write current info to guess.json
        write_json(data, style.guess_path)
        
        embed = get_guess_embed(start, end, price)

        await ctx.followup.send(embed=embed)

    @client.tree.command(name=style.command_guess_info_name_text, description=style.command_guess_info_description_text, guild=discord.Object(id=env_vars['guild_id']))
    async def guess_info(ctx: discord.Interaction):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(style.admin_error_text, ephemeral=True)
            return

        # Defer the response (shows bot is thinking)
        await ctx.response.defer(ephemeral=True)
        
        data, load_error = load_json(style.guess_path)
        if load_error or data == {}:
            await ctx.followup.send(style.guess_error_text.format(load_error), ephemeral=True)
            return
        
        await ctx.followup.send(str(data), ephemeral=True)

    @client.tree.command(name=style.command_guess_end_name_text, description=style.command_guess_end_description_text, guild=discord.Object(id=env_vars['guild_id']))
    async def guess_end(ctx: discord.Interaction):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(style.admin_error_text, ephemeral=True)
            return

        await ctx.response.defer(ephemeral=True)
        await handle_guess_end(ctx)

    @client.tree.command(name=style.command_guess_name_text, description=style.command_guess_description_text, guild=discord.Object(id=env_vars['guild_id']))
    async def guess(ctx: discord.Interaction, number: int):
        await ctx.response.defer(ephemeral=True)
        
        if ctx.channel.id == env_vars['channel_id']:
            await ctx.followup.send(style.guess_wrong_channel_text)
            return
        
        if not os.path.isfile(style.guess_path):
            await ctx.followup.send(style.guess_no_active_competition, ephemeral=True)
            return
        
        data, load_error = load_json(style.guess_path)
        if load_error:
            await ctx.followup.send(style.guess_error_text.format(""), ephemeral=True)
            return
        
        data['participants'] += 1
        winner_number = data.get('winner_number')
        price = data.get('price')
        
        if number == winner_number:
            embed = get_winner_embed(ctx.user.mention, price, winner_number)
            await handle_guess_end(ctx)
            await ctx.followup.send(embed=embed)
            return
        
        write_json(data, style.guess_path)
        await ctx.followup.send(style.guess_better_luck_text)
        
        

def run() -> None:
    """called to start the bot
    """
    global env_vars, FILE_PATH
    env_vars = load_env_vars()
    FILE_PATH = os.path.join(os.curdir, env_vars["path_to_json"])
    register_commands()

    client.activity=discord.Activity(type=discord.ActivityType(3), name=env_vars['activity_text'])
    client.run(env_vars["discord_token"])

if __name__ == "__main__":
    run()
