import discord
from gemini import generate_plan_with_gemini

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

    # Check if the message starts with the command `!plan`
    if message.content.startswith('!plan'):
        # Let the user know the bot is working on it
        await message.channel.send("Got it! I'm thinking and creating a plan for you. This might take a moment...")

        # Extract the content of the message after the `!plan ` command
        # It's better to ask the user to format their request clearly.
        # Example usage: !plan Goal: Learn Python | Current Situation: I know basic HTML, I have 3 months.
        try:
            # We expect the user to separate the goal and situation with a pipe symbol `|`
            query = message.content[6:].strip() # Get everything after "!plan "
            goal_part, situation_part = query.split('|', 1)

            # Clean up the input strings
            goal = goal_part.replace("Goal:", "").strip()
            situation = situation_part.replace("Current Situation:", "").strip()

            if not goal or not situation:
                await message.channel.send("Please provide both a goal and your current situation. Example: `!plan Goal: Run a 5k | Current Situation: I can run for 5 minutes, I have 2 months.`")
                return

            # Call the Gemini function to generate the plan
            plan = await generate_plan_with_gemini(goal, situation)

            # Send the generated plan back to the Discord channel
            # Discord has a 2000 character limit per message. For longer plans,
            # you might need to split the message into parts.
            if len(plan) > 2000:
                await message.channel.send("The plan is quite long! Here it is in parts:")
                for i in range(0, len(plan), 2000):
                    await message.channel.send(plan[i:i+2000])
            else:
                await message.channel.send(plan)

        except ValueError:
            # This happens if the user doesn't use the '|' separator
            await message.channel.send("Please use the correct format. Separate your goal and situation with a `|`. \nExample: `!plan Goal: Learn Python | Current Situation: Total beginner, 2 hours available per day`")
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")
