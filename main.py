import os
from dotenv import load_dotenv
import discord
import google.generativeai as genai

# Import the 'client' object from our bot.py file
from bot import client

# --- SETUP AND RUN ---
def main():
    """
    Main function to load configs and run the bot.
    """
    # Load environment variables from the .env file
    load_dotenv()
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Check if the keys are available
    if not DISCORD_BOT_TOKEN or not GEMINI_API_KEY:
        print("ERROR: Make sure you have created a .env file with your DISCORD_BOT_TOKEN and GEMINI_API_KEY")
        return

    # Configure the Gemini API
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"ERROR: Could not configure Gemini API: {e}")
        return

    # Run the bot
    try:
        client.run(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("ERROR: Failed to log in. Please check your DISCORD_BOT_TOKEN.")
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")


# This is the entry point of the script.
if __name__ == "__main__":
    main()
