import discord;
from discord.ext import commands;
import json;
import aiohttp;
import os;
import re;
import dotenv;
import copy;

#load the dotenv file
dotenv.load_dotenv()

# Load the environment variables
base_config_path =os.getenv('OPEN_AI_CONFIG_FILE_LOC')
config_file = os.path.normpath(os.path.join(base_config_path,'openai_config.json'))
item_config = os.path.normpath(os.path.join(base_config_path,'openai_items_config.json'))
enemies_config = os.path.normpath(os.path.join(base_config_path,'openai_enemies_config.json'))
credits_config = os.path.normpath(os.path.join(base_config_path,'credits.json'))
discord_desc_config = os.path.normpath(os.path.join(base_config_path,'openai_discord_descriptions.json'))
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BOT_NAME = os.getenv("BOTNAME")
VERSION = os.getenv("VERSION")
PRIMARY_EMBED_COLOR = int(os.getenv("EMBED_COLOR"),16)
OPENAI_KEY= os.getenv("OPENAI_API_KEY")


smile = "\U0001F600"
frown = "\U0001F641"
heart = "🩷"

with open(config_file) as config_file:
    ass_config = json.load(config_file)
with open(item_config) as item_file:
    ass_items_config = json.load(item_file)

with open(enemies_config) as enemy_file:
    ass_enemy_config = json.load(enemy_file)

with open(credits_config) as credit_file:
    app_friends = json.loads(credit_file.read())
with open(discord_desc_config) as discord_desc_file:
    disc_desc_conf = json.loads(discord_desc_file.read())


friend_string = ""
for friend in app_friends['friends']:
    friend_string = friend_string + "\n" + friend + " " + heart




# Create a bot instance with a command prefix
intents = discord.Intents.default()
intents.message_content =True;
intents.members = True;
bot = commands.Bot(command_prefix='.',intents=intents)
client = discord.Client (intents=intents)


def remove_special_characters(string:str):
    allowed_characters = re.compile(r'[a-zA-Z0-9_\-\.]+') #regex to allow only alphanumeric characters and _ - . characters
    #its easier to find the allowed characters than to find the disallowed characters also i hate regex with a passion

    # Use the findall method to get a list of allowed character sequences
    allowed_parts = re.findall(allowed_characters, string)

    # Join the allowed parts to form the cleaned file name
    cleaned_string = ''.join(allowed_parts)
    return cleaned_string


# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    #print(os.getcwd())

    await bot.tree.sync()
@bot.tree.command(name="myfriends",description="These people inspired my creator to make me ")
async def myfriends(interaction:discord.Interaction):

    embed = discord.Embed(title="My Friends " + smile, color=PRIMARY_EMBED_COLOR)
    embed.add_field(name="This is my Name " + heart , value=BOT_NAME, inline=True)
    embed.add_field(name="Version", value=VERSION, inline=True)
    embed.add_field(name="Author", value="Scott/itachi/ZERO", inline=True)
    embed.add_field(name="Friends", value=friend_string, inline=False)
    embed.add_field(name="Thank you for helping to bring me into reality " + heart + heart + heart , value=BOT_NAME, inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="version",description="Get"+ BOT_NAME +" bot version")
async def version(interaction:discord.Interaction):
    embed = discord.Embed(title="My Version Info :D ", color=PRIMARY_EMBED_COLOR)
    embed.add_field(name="This is my Name :) ", value=BOT_NAME, inline=True)
    embed.add_field(name="Version", value=VERSION, inline=True)
    embed.add_field(name="Author", value="Scott/itachi", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="create_charachter",description="Give your charachter info e.g greg the bowler from taiwan")
async def create_charachter(interaction:discord.Interaction, * ,charachter_info:str):
    try :
        await interaction.response.defer()
        open_ai_key = OPENAI_KEY
        if open_ai_key is None:
           print('No openai key found')
           return None

        message_length = len(charachter_info)
    #if the message is longer than 2000 characters then just return an error
        if message_length > 2000:
            response = {}
            response['message_error'] = "Message is too long"
            return(response)
        #if the message is empty then just return an error
        if message_length == 0:
            response = {}
            response['message_error'] = "Message is empty"
            return(response)
        if message_length >= 256:
            message = message[:128] + '....' #truncate the message to 128 characters and add .... to the end discord embeds can only hold 256 characters
            #i may intro nltk to summarize the message later mabee but this is close nuff for now
        data = []
        data =  copy.deepcopy(ass_config)
        data['messages'].append({"role": "user","content": charachter_info})
        #write data to file
        """ with open("data.json", 'w', encoding='utf-8') as f:
            json.dump(data,f) """
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/chat/completions', json=data,
                headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ OPENAI_KEY,
                }) as resp:
                if resp.status != 200:
                    response = {}
                    response['message_error'] = "Could not get response"
                    #return(response)
                response = await resp.json()
                if("message_error" in response):
                    return await interaction.followup.send(response['message_error'])
                elif("error" in response):
                    raise Exception(response['error'])
                else:
                    reply = response['choices'][0]['message']['content']
                    embed = discord.Embed(title=charachter_info, color=PRIMARY_EMBED_COLOR)
                    #if reply is greater than or equal to 1024 characters then split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                    if len(reply) >= 1024:
                        #split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                        #get the number of messages
                        message_count = len(reply) // 1024 #Divide the length of the reply by 1024 and get the integer // does not keep the remainder
                        #get the remainder
                        remainder = len(reply) % 1024
                        #if there is a remainder then add 1 to the message count
                        if remainder > 0:
                            message_count = message_count + 1
                        #split the reply into n messages
                        #create a list to hold the messages
                        messages = []
                        #create a counter
                        counter = 0
                        #create a variable to hold the start position
                        start = 0
                        #create a variable to hold the end position
                        end = 1024
                        #loop through the message count and append the message to the messages list
                        while counter < message_count:
                            #append the message to the messages list
                            messages.append(reply[start:end])
                            #increment the counter
                            counter = counter + 1
                            #increment the start position
                            start = start + 1024
                            #increment the end position
                            end = end + 1024
                        #loop through the messages list and send each message
                        for message in messages:
                            embed.add_field(name=" ", value=message, inline=True)
                        #send the embed
                    else:
                        embed.add_field(name=" ", value=reply, inline=True)
                    await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occured, please try again later.")
        return None


@bot.tree.command(name="create_item",description="Give your item some info e.g sword of awesome or health potion")
async def create_charachter(interaction:discord.Interaction, * ,item_info:str):
    try :
        await interaction.response.defer()
        open_ai_key = OPENAI_KEY
        if open_ai_key is None:
           print('No openai key found')
           return None

        message_length = len(item_info)
    #if the message is longer than 2000 characters then just return an error
        if message_length > 2000:
            response = {}
            response['message_error'] = "Message is too long"
            return(response)
        #if the message is empty then just return an error
        if message_length == 0:
            response = {}
            response['message_error'] = "Message is empty"
            return(response)
        if message_length >= 256:
            message = message[:128] + '....' #truncate the message to 128 characters and add .... to the end discord embeds can only hold 256 characters
            #i may intro nltk to summarize the message later mabee but this is close nuff for now
        data = []
        data =  copy.deepcopy(ass_items_config)
        data['messages'].append({"role": "user","content": item_info})
        #write data to file
        """ with open("data.json", 'w', encoding='utf-8') as f:
            json.dump(data,f) """
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/chat/completions', json=data,
                headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ OPENAI_KEY,
                }) as resp:
                if resp.status != 200:
                    response = {}
                    response['message_error'] = "Could not get response"
                    #return(response)
                response = await resp.json()
                if("message_error" in response):
                    return await interaction.followup.send(response['message_error'])
                elif("error" in response):
                    raise Exception(response['error'])
                else:
                    reply = response['choices'][0]['message']['content']
                    embed = discord.Embed(title=item_info, color=PRIMARY_EMBED_COLOR)
                    #if reply is greater than or equal to 1024 characters then split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                    if len(reply) >= 1024:
                        #split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                        #get the number of messages
                        message_count = len(reply) // 1024 #Divide the length of the reply by 1024 and get the integer // does not keep the remainder
                        #get the remainder
                        remainder = len(reply) % 1024
                        #if there is a remainder then add 1 to the message count
                        if remainder > 0:
                            message_count = message_count + 1
                        #split the reply into n messages
                        #create a list to hold the messages
                        messages = []
                        #create a counter
                        counter = 0
                        #create a variable to hold the start position
                        start = 0
                        #create a variable to hold the end position
                        end = 1024
                        #loop through the message count and append the message to the messages list
                        while counter < message_count:
                            #append the message to the messages list
                            messages.append(reply[start:end])
                            #increment the counter
                            counter = counter + 1
                            #increment the start position
                            start = start + 1024
                            #increment the end position
                            end = end + 1024
                        #loop through the messages list and send each message
                        for message in messages:
                            embed.add_field(name=" ", value=message, inline=True)
                        #send the embed
                    else:
                        embed.add_field(name=" ", value=reply, inline=True)
                    await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occured, please try again later.")
        return None

@bot.tree.command(name="create_enemy",description="Give your enemy some info e.g night bat")
async def create_enemy(interaction:discord.Interaction, * ,enemy_info:str):
    try :
        await interaction.response.defer()
        open_ai_key = OPENAI_KEY
        if open_ai_key is None:
           print('No openai key found')
           return None

        message_length = len(enemy_info)
    #if the message is longer than 2000 characters then just return an error
        if message_length > 2000:
            response = {}
            response['message_error'] = "Message is too long"
            return(response)
        #if the message is empty then just return an error
        if message_length == 0:
            response = {}
            response['message_error'] = "Message is empty"
            return(response)
        if message_length >= 256:
            message = message[:128] + '....' #truncate the message to 128 characters and add .... to the end discord embeds can only hold 256 characters
            #i may intro nltk to summarize the message later mabee but this is close nuff for now
        data = []
        data =  copy.deepcopy(ass_enemy_config)
        data['messages'].append({"role": "user","content": enemy_info})
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/chat/completions', json=data,
                headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ OPENAI_KEY,
                }) as resp:
                if resp.status != 200:
                    response = {}
                    response['message_error'] = "Could not get response"
                    #return(response)
                response = await resp.json()
                if("message_error" in response):
                    return await interaction.followup.send(response['message_error'])
                elif("error" in response):
                    raise Exception(response['error'])
                else:
                    reply = response['choices'][0]['message']['content']
                    embed = discord.Embed(title=enemy_info, color=PRIMARY_EMBED_COLOR)
                    #if reply is greater than or equal to 1024 characters then split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                    if len(reply) >= 1024:
                        #split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                        #get the number of messages
                        message_count = len(reply) // 1024 #Divide the length of the reply by 1024 and get the integer // does not keep the remainder
                        #get the remainder
                        remainder = len(reply) % 1024
                        #if there is a remainder then add 1 to the message count
                        if remainder > 0:
                            message_count = message_count + 1
                        #split the reply into n messages
                        #create a list to hold the messages
                        messages = []
                        #create a counter
                        counter = 0
                        #create a variable to hold the start position
                        start = 0
                        #create a variable to hold the end position
                        end = 1024
                        #loop through the message count and append the message to the messages list
                        while counter < message_count:
                            #append the message to the messages list
                            messages.append(reply[start:end])
                            #increment the counter
                            counter = counter + 1
                            #increment the start position
                            start = start + 1024
                            #increment the end position
                            end = end + 1024
                        #loop through the messages list and send each message
                        for message in messages:
                            embed.add_field(name=" ", value=message, inline=True)
                        #send the embed
                    else:
                        embed.add_field(name=" ", value=reply, inline=True)
                    await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occured, please try again later.")
        return None

@bot.tree.command(name="create_profile_description",description="make a description for your discord profile rpg style")
async def create_profile_desc(interaction:discord.Interaction):
    try :
        await interaction.response.defer()
        open_ai_key = OPENAI_KEY
        if open_ai_key is None:
           print('No openai key found')
           return None
       #get users guild id
        guild_id = interaction.guild_id
        #find the usrs guild name
        guild = await bot.fetch_guild(guild_id)

        user = await guild.fetch_member(interaction.user.id)
        #print(user)
        charachter_info = str(user.display_name)
        message_length = len(charachter_info)
    #if the message is longer than 2000 characters then just return an error
        if message_length > 2000:
            response = {}
            response['message_error'] = "Message is too long"
            return(response)
        #if the message is empty then just return an error
        if message_length == 0:
            response = {}
            response['message_error'] = "Message is empty"
            return(response)
        if message_length >= 256:
            message = message[:128] + '....' #truncate the message to 128 characters and add .... to the end discord embeds can only hold 256 characters
            #i may intro nltk to summarize the message later mabee but this is close nuff for now
        data = []
        data =  copy.deepcopy(disc_desc_conf)
        #print(charachter_info)
        data['messages'].append({"role": "user","content": charachter_info})
        #write data to file
        """ with open("data.json", 'w', encoding='utf-8') as f:
            json.dump(data,f) """
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/chat/completions', json=data,
                headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ OPENAI_KEY,
                }) as resp:
                if resp.status != 200:
                    response = {}
                    response['message_error'] = "Could not get response"
                    #return(response)
                response = await resp.json()
                if("message_error" in response):
                    return await interaction.followup.send(response['message_error'])
                elif("error" in response):
                    raise Exception(response['error'])
                else:
                    reply = response['choices'][0]['message']['content']
                    embed = discord.Embed(title=charachter_info, color=PRIMARY_EMBED_COLOR)
                    #if reply is greater than or equal to 1024 characters then split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                    if len(reply) >= 1024:
                        #split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                        #get the number of messages
                        message_count = len(reply) // 1024 #Divide the length of the reply by 1024 and get the integer // does not keep the remainder
                        #get the remainder
                        remainder = len(reply) % 1024
                        #if there is a remainder then add 1 to the message count
                        if remainder > 0:
                            message_count = message_count + 1
                        #split the reply into n messages
                        #create a list to hold the messages
                        messages = []
                        #create a counter
                        counter = 0
                        #create a variable to hold the start position
                        start = 0
                        #create a variable to hold the end position
                        end = 1024
                        #loop through the message count and append the message to the messages list
                        while counter < message_count:
                            #append the message to the messages list
                            messages.append(reply[start:end])
                            #increment the counter
                            counter = counter + 1
                            #increment the start position
                            start = start + 1024
                            #increment the end position
                            end = end + 1024
                        #loop through the messages list and send each message
                        for message in messages:
                            embed.add_field(name=" ", value=message, inline=True)
                        #send the embed
                    else:
                        embed.add_field(name=" ", value=reply, inline=True)
                    await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occured, please try again later.")
        return None

@bot.tree.command(name="create_my_discord_charachter",description="make a description for your discord user rpg style")
async def create_disc_rpg_profile(interaction:discord.Interaction):
    try :
        await interaction.response.defer()
        open_ai_key = OPENAI_KEY
        if open_ai_key is None:
           print('No openai key found')
           return None
       #get users guild id
        guild_id = interaction.guild_id
        #find the usrs guild name
        guild = await bot.fetch_guild(guild_id)

        user = await guild.fetch_member(interaction.user.id)
        #print(user)
        charachter_info = str(user.display_name)
        message_length = len(charachter_info)
    #if the message is longer than 2000 characters then just return an error
        if message_length > 2000:
            response = {}
            response['message_error'] = "Message is too long"
            return(response)
        #if the message is empty then just return an error
        if message_length == 0:
            response = {}
            response['message_error'] = "Message is empty"
            return(response)
        if message_length >= 256:
            message = message[:128] + '....' #truncate the message to 128 characters and add .... to the end discord embeds can only hold 256 characters
            #i may intro nltk to summarize the message later mabee but this is close nuff for now
        data = []
        data =  copy.deepcopy(ass_config)
        #print(charachter_info)
        data['messages'].append({"role": "user","content": charachter_info})
        #write data to file
        """ with open("data.json", 'w', encoding='utf-8') as f:
            json.dump(data,f) """
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/chat/completions', json=data,
                headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ OPENAI_KEY,
                }) as resp:
                if resp.status != 200:
                    response = {}
                    response['message_error'] = "Could not get response"
                    #return(response)
                response = await resp.json()
                if("message_error" in response):
                    return await interaction.followup.send(response['message_error'])
                elif("error" in response):
                    raise Exception(response['error'])
                else:
                    reply = response['choices'][0]['message']['content']
                    embed = discord.Embed(title=charachter_info, color=PRIMARY_EMBED_COLOR)
                    #if reply is greater than or equal to 1024 characters then split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                    if len(reply) >= 1024:
                        #split the reply into n messages where n is the number of times 1024 goes into the length of the reply
                        #get the number of messages
                        message_count = len(reply) // 1024 #Divide the length of the reply by 1024 and get the integer // does not keep the remainder
                        #get the remainder
                        remainder = len(reply) % 1024
                        #if there is a remainder then add 1 to the message count
                        if remainder > 0:
                            message_count = message_count + 1
                        #split the reply into n messages
                        #create a list to hold the messages
                        messages = []
                        #create a counter
                        counter = 0
                        #create a variable to hold the start position
                        start = 0
                        #create a variable to hold the end position
                        end = 1024
                        #loop through the message count and append the message to the messages list
                        while counter < message_count:
                            #append the message to the messages list
                            messages.append(reply[start:end])
                            #increment the counter
                            counter = counter + 1
                            #increment the start position
                            start = start + 1024
                            #increment the end position
                            end = end + 1024
                        #loop through the messages list and send each message
                        for message in messages:
                            embed.add_field(name=" ", value=message, inline=True)
                        #send the embed
                    else:
                        embed.add_field(name=" ", value=reply, inline=True)
                    await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occured, please try again later.")
        return None











@bot.tree.command(name="helpme",description="Get some help")
async def helpme(interaction:discord.Interaction):
    embed = discord.Embed(title="Help", color=PRIMARY_EMBED_COLOR)
    embed.add_field(name="Version", value="Get the version of the bot", inline=True)
    embed.add_field(name="Create Charachter", value="Create a charachter", inline=True)
    await interaction.response.send_message(embed=embed)


# Run the bot with the token
bot.run(TOKEN)
