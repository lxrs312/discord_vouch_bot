import discord
from discord.ext import commands
from discord import app_commands
import localconfig as lf
from datetime import datetime
import stylesheet as style
import json
import os

FILE_PATH = os.path.join(os.curdir, lf.path_to_json)

STAR_CHOICES = [
    app_commands.Choice(name="⭐", value=1),
    app_commands.Choice(name="⭐⭐", value=2),
    app_commands.Choice(name="⭐⭐⭐", value=3),
    app_commands.Choice(name="⭐⭐⭐⭐", value=4),
    app_commands.Choice(name="⭐⭐⭐⭐⭐", value=5),
]

intents = discord.Intents.default()
client = commands.Bot(command_prefix=None, intents=intents, activity=discord.Activity(type=discord.ActivityType(3), name=lf.activity_text))

def write_json(data: dict) -> str:
    try:
        with open(FILE_PATH, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return f"Error writing to the JSON file: {e}"


def load_json() -> tuple[dict, str]:
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r', encoding="utf8") as file:
                return json.load(file), ""
        except json.JSONDecodeError as e:
            return {}, f"Error reading JSON file: {e}"
    else:
        return {}, ""


def get_embed(star_string: str, comment: str, new_vouch_nr: int, user: discord.User, image: discord.Attachment) -> discord.Embed:
    now = datetime.now()
    embed = discord.Embed(title=style.vouch_title_text, description=star_string, colour=style.color, timestamp=now)
    embed.add_field(name=style.vouch_comment_text, value=comment, inline=False)
    embed.add_field(name=style.vouch_nr_text, value=new_vouch_nr, inline=True)
    embed.add_field(name=style.vouch_by_text, value=f"{user.mention}", inline=True)
    embed.set_thumbnail(url=user.display_avatar)
    embed.set_footer(text=client.user.name, icon_url=lf.icon_url)
    embed.set_image(url=image.url)

    return embed

@client.event
async def on_ready():
    await client.tree.sync(guild=discord.Object(id=lf.guild_id))  

@client.tree.command(name=style.command_name_text, description=style.command_description_text, guild=discord.Object(id=lf.guild_id))
@app_commands.describe(stars=style.command_stars_description_text, comment=style.command_comment_description_text, image=style.command_image_description_text)
@app_commands.choices(stars=STAR_CHOICES)
async def vouch(ctx: discord.Interaction, stars: app_commands.Choice[int], comment: str, image: discord.Attachment):
    await ctx.response.defer(thinking=True)
    
    if ctx.channel_id != lf.channel_id:
        await ctx.followup.send(style.wrong_channel_error_text)
        return

    # load data
    data, load_error = load_json()
    if load_error:
        await ctx.followup.send(style.save_json_error_text.format(load_error), ephemeral=True)
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
        await ctx.followup.send(style.image_error_text, ephemeral=True)
        return

    embed = get_embed(star_string, comment, new_vouch_nr, ctx.user, image)

    # add new entry
    data[new_vouch_nr] = {
        "date": now.strftime(style.date_format),
        "comment": comment,
        "user": ctx.user.id,
        "stars": stars.value
    }

    # write data
    write_error = write_json(data)
    if write_error:
        await ctx.followup.send(style.save_json_error_text.format(write_error), ephemeral=True)
        return

    # change channel name to account for new_vouch
    await ctx.channel.edit(name=style.vouch_channel_name.format(new_vouch_nr))
    
    # sendit
    await ctx.followup.send(embed=embed)

client.run(lf.discord_auth_token)
