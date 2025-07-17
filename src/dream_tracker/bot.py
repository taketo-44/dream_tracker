import discord
from gemini import generate_plan_with_gemini, generate_todo_with_gemini, generate_motivator_with_gemini
from database import save_user_data, get_user_data

# Set up the bot's intents. Intents define what events the bot receives from Discord.
# We need the message_content intent to read the user's messages.
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create a bot instance. This 'client' will be imported by main.py
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """
    This function runs when the bot has successfully connected to Discord.
    """
    print(f'Bot is ready and logged in as {client.user}')

@client.event
async def on_message(message):
    """
    This function runs every time a message is sent in a channel the bot can see.
    """
    # Ignore messages sent by the bot itself to prevent loops
    if message.author == client.user:
        return

    user_id = str(message.author.id)

    if message.content.startswith('!goal'):
        #set a goal to achieve and save the goal into the database
        await message.channel.send("Got it! I'm saving a goal to achieve")
        try:
            # Extract the content of the message after the `!goal ` command
            goal = message.content[6:].strip()  # Get everything after "!goal "
            if not goal:
                await message.channel.send("Please provide a goal. Example: `!goal Run a marathon`")
                return
            #save the goal to the database
            save_user_data(user_id, {'goal': goal})

        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")
    
    if message.content.startswith('!situation'):
        #set a current situation
        await message.channel.send("Got it! I'm updating your current situation. This might take a moment...")
        try:
            # Extract the content of the message after the `!situation ` command
            situation = message.content[11:].strip()  # Get everything after "!situation "
            if not situation:
                await message.channel.send("Please provide a situation. Example: `!situation I have 3 months to prepare`")
                return

            #save the situation to the database
            save_user_data(user_id, {'situation': situation})
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")
    
    if message.content.startswith('!show'):
        #show current goal and situation
        await message.channel.send("Here is your current goal and situation:")
        try:
            # Retrieve the goal and situation from the database
            user_data = get_user_data(user_id)
            goal = user_data['goal'] if 'goal' in user_data else 'Nothing added so far'
            situation = user_data['situation'] if 'situation' in user_data else 'Nothing added so far'
            
            if not goal or not situation:
                await message.channel.send("You haven't set a goal or situation yet. Use `!goal` and `!situation` to set them.")
                return
            
            response = f"**Current Goal:** {goal}\n**Current Situation:** {situation}"
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")
        
    if message.content.startswith('!plan'):
        await message.channel.send("Generating your plan based on your goal and situation. This might take a moment...")
        try:
            user_data = get_user_data(user_id)
            goal = user_data.get('goal', '') if user_data else ''
            situation = user_data.get('situation', '') if user_data else ''

            if not goal or not situation:
                await message.channel.send(
                    "I need both a goal and a situation to generate a plan. "
                    "Please set your goal with `!goal [your goal]` and your situation with `!situation [your situation]`."
                )
                return

            plan = await generate_plan_with_gemini(goal, situation)
            if len(plan) > 2000:
                await message.channel.send("The plan is quite long! Here it is in parts:")
                for i in range(0, len(plan), 2000):
                    await message.channel.send(plan[i:i+2000])
            else:
                await message.channel.send(plan)

        except Exception as e:
            await message.channel.send(f"An unexpected error occurred while generating your plan: {e}")
    
    if message.content.startswith('!todo'):
        await message.channel.send("Generating a to-do list based on your goal and situation. This might take a moment...")
        try:
            user_data = get_user_data(user_id)
            goal = user_data.get('goal', '') if user_data else ''
            situation = user_data.get('situation', '') if user_data else ''

            if not goal or not situation:
                await message.channel.send(
                    "I need both a goal and a situation to generate a to-do list. "
                    "Please set them using `!goal [your goal]` and `!situation [your situation]`."
                )
                return

            todo_list = await generate_todo_with_gemini(goal, situation)
            if len(todo_list) > 2000:
                await message.channel.send("The to-do list is quite long! Here it is in parts:")
                for i in range(0, len(todo_list), 2000):
                    await message.channel.send(todo_list[i:i+2000])
            else:
                await message.channel.send(todo_list)

        except Exception as e:
            await message.channel.send(f"An unexpected error occurred while generating your to-do list: {e}")