import discord
from gemini import generate_plan_with_gemini, generate_todo_with_gemini, generate_motivator_with_gemini

try:
    # Attempt to get the path from an environment variable for better security

    # Example: SERVICE_ACCOUNT_KEY_PATH = 'path/to/your/serviceAccountKey.json'
    SERVICE_ACCOUNT_KEY_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')

    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print(f"ERROR: Firebase service account key not found at {SERVICE_ACCOUNT_KEY_PATH}")
        db = None # Set db to None if initialization fails
    else:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")

except Exception as e:
    print(f"ERROR: Could not initialize Firebase: {e}")
    db = None # Set db to None if initialization fails

USERS_COLLECTION = 'discord_users'

# --- Function to Save User Data ---
def save_user_data(user_id: str, data: dict):
    """
    Saves or updates data for a specific Discord user in Firestore.

    Args:
        user_id (str): The unique Discord user ID. This will be the document ID.
        data (dict): A dictionary containing the user's information.
                     Example: {'goal': 'Run a marathon', 'situation': '3 months to prepare'}
    """
    if db is None:
        print("Database not initialized. Cannot save data.")
        return
    try:
        user_doc_ref = db.collection(USERS_COLLECTION).document(user_id)
        # merge=True allows updating specific fields without overwriting the whole document
        user_doc_ref.set(data, merge=True)
        print(f"Data for user '{user_id}' saved successfully: {data}")
    except Exception as e:
        print(f"Error saving data for user '{user_id}': {e}")

# --- Function to Get User Data ---
def get_user_data(user_id: str):
    """
    Retrieves data for a specific Discord user from Firestore.

    Args:
        user_id (str): The unique Discord user ID.

    Returns:
        dict or None: A dictionary containing the user's data if found, otherwise None.
    """
    if db is None:
        print("Database not initialized. Cannot retrieve data.")
        return None
    try:
        user_doc_ref = db.collection(USERS_COLLECTION).document(user_id)
        doc = user_doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"Data for user '{user_id}' retrieved successfully: {data}")
            return data
        else:
            print(f"No data found for user '{user_id}'.")
            return None
    except Exception as e:
        print(f"Error retrieving data for user '{user_id}': {e}")
        return None


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

    if message.content.startswith('!goal'):
        #set a goal to achieve and save the goal into the database
        await message.channel.send("Got it! I'm updating a goal and creating a long, mid and short term goals for you. This might take a moment...")
        try:
            # Extract the content of the message after the `!goal ` command
            goal = message.content[6:].strip()  # Get everything after "!goal "
            if not goal:
                await message.channel.send("Please provide a goal. Example: `!goal Run a marathon`")
                return

            # Send the generated plan back to the Discord channel
            if len(plan) > 2000:
                await message.channel.send("The plan is quite long! Here it is in parts:")
                for i in range(0, len(plan), 2000):
                    await message.channel.send(plan[i:i+2000])
            else:
                await message.channel.send(plan)
            
            #save the goal to the database

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
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")
    
    if message.content.startswith('!show'):
        #show current goal and situation
        await message.channel.send("Here is your current goal and situation:")
        try:
            # Retrieve the goal and situation from the database
            goal = "" # Replace with data saved in the database
            situation = "" # Replace with data saved in the database
            
            if not goal or not situation:
                await message.channel.send("You haven't set a goal or situation yet. Use `!goal` and `!situation` to set them.")
                return
            
            response = f"**Current Goal:** {goal}\n**Current Situation:** {situation}"
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"An unexpected error occurred: {e}")