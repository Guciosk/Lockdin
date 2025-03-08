# Discord DM Bot

A Discord bot that can send direct messages to users by their ID and read all messages from those DMs, including new ones as they come in.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Discord bot token and target user ID:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   TARGET_USER_ID=your_target_user_id_here
   ```
4. Run the bot:
   ```
   python app.py
   ```

## How to Get a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the bot's username, click "Reset Token" and copy the new token
5. Paste this token in your `.env` file

## Required Bot Permissions

When adding the bot to your server, make sure it has the following permissions:
- Read Messages/View Channels
- Send Messages
- Read Message History

## Bot Intents

This bot requires the following intents to be enabled in the Discord Developer Portal:
- Message Content Intent
- Server Members Intent

## Commands

- `!dm <user_id> <message>` - Send a direct message to a user by their ID
- `!list_dms` - List all active DM channels
- `!read_dm <user_id> [limit]` - Read the DM history with a specific user (default limit: 10 messages)

## Features

- Send DMs to users by their Discord ID
- Automatically read and log all incoming DMs
- View message history with specific users
- List all active DM channels
- Automatically send "Hello World" every 5 seconds to a specified target user

## Automatic Messaging

The bot will automatically send "Hello World" every 5 seconds to the user specified by the TARGET_USER_ID in your .env file. This feature starts as soon as the bot connects to Discord.

## Note

The bot will automatically log all DM messages to the console. To see these logs, check the terminal where the bot is running. 