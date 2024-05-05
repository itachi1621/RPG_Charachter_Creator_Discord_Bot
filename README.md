# RPG Character Maker

This Discord bot allows you to create RPG character descriptions using OpenAI's natural language processing capabilities. You can generate unique character backgrounds, traits, and more with just a simple command.

## How to Use
To interact with the RPG Character Maker bot, use the following commands in your Discord server:

- /version: Get information about the bot's version.
- /create_character: Create a character by providing a  character description, like Greg the bowler from Taiwan.
- /helpme: Get help on how to use the bot.

## Setup
Follow these steps to set up the Discord bot:

1. Create a Discord Bot
Go to the Discord Developer Portal.
Click on New Application.
Give your application a name (e.g., RPG Character Maker).
Go to the Bot tab on the left sidebar and click Add Bot.
Click on Copy Token under the bot username to get your DISCORD_BOT_TOKEN.
2. Enable Intents
Still in the Developer Portal, navigate to the Bot tab.
Under Privileged Gateway Intents, enable the following intents:
- Message Intent
3. Set Environment Variables
Create a .env file in the project directory with the following variables:
```bash
OPENAI_API_KEY = ""
DISCORD_BOT_TOKEN=""
OPEN_AI_CONFIG_FILE_LOC="configs/openai_config.json USE FULL PATH to file not relative e,g C:/USers/SAM etc.. or /home/sam...."
BOTNAME = "RPG Charahcter Maker"
VERSION = "1.0.3"
EMBED_COLOR = "0x0000FF"
```
4. Install Dependencies
Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```
5. Run the Bot
Start the bot by running the following command in your terminal:

```bash
python RPF_Bot.py
```
## Additional Notes
The bot uses OpenAI's GPT-3 model to generate character descriptions based on the provided input.
Make sure to provide a clear and concise character description to get the best results.
Feel free to contribute to this project and customize the bot according to your needs. Happy character creating! 🎲



