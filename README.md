# Discord Vouch Bot

## Overview

The Discord Vouch Bot is a Discord bot built using `discord.py` that allows users to leave "vouches" for the server. These vouches are tracked, saved, and displayed in a channel on a Discord server. This bot can handle vouches with varying star ratings and includes features for embedding the vouch data in messages. It is designed to integrate seamlessly with Discord's slash commands and activity features.

## Features

- **Vouch Commands**: Allows users to submit vouches with star ratings and messages.
- **Embed Messages**: Displays vouches in an embedded message format with user information and images.
- **Channel Validation**: Ensures commands are used in the correct channel.
- **Persistent Data**: Saves and loads vouch data from a JSON file.

## Setup Instructions

### 1. Fork the Repository

### 2. Clone Your Forked Repository

Clone your forked repository to your local machine:

```bash
git clone https://github.com/yourusername/discord_vouch_bot.git
cd discord_vouch_bot
```

### 3. Create and Configure the .env File

1. Create a file named .env in the root of your project directory.
2. Add the following environment variables to the .env file:

```env
DISCORD_AUTH_TOKEN=your_discord_auth_token
GUILD_ID=your_guild_id
ICON_URL=your_icon_url
ACTIVITY_TEXT=your_activity_text
PATH_TO_JSON=path_to_your_json_file
CHANNEL_ID=your_channel_id
```

### 4. Set Up AWS Deployment (optional)

1. List item Generate SSH-keys
2.  Add keys to GitHub secrets

```env
AWS_HOST
AWS_PATH
AWS_SSH_PRIVATE_KEY
AWS_USER
```

3. Configure GitHub Actions Workflow

### 5. Install Dependencies
```python
python -m venv bot-env
source bot-env/bin/activate
pip install -r requirements.txt
```

### 6. Run the Bot Locally (Optional)

```python
python main.py
```

### Contributing

If you'd like to contribute to the project, please submit a pull request or open an issue to discuss changes.


