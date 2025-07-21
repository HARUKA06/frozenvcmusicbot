import logging
import yt_dlp as youtube_dl
import random
import requests
from telegram import Update, InputTextMessageContent, ChatMember
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import time

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = "YOUR_BOT_TOKEN"

# Path for temporary audio storage
TEMP_DIR = "/tmp/musicbot"

# Create necessary directories if not exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Dictionary to keep track of AFK users
afk_users = {}

# Variables to store music state
current_voice_message = None
current_audio_file = None
is_paused = False
paused_audio_file = None

# Fun commands data (for example)
jokes = [
    "Why don't skeletons fight each other? They don't have the guts.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "I asked the librarian if the library had any books on paranoia. She whispered, 'They're right behind you.'"
]

quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson"
]

# Helper to download the audio from YouTube or other sources
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(TEMP_DIR, 'music.%(ext)s'),
        'noplaylist': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# Music Commands (Already Included)
# Command to play music from a YouTube link
def play(update: Update, context: CallbackContext) -> None:
    global current_voice_message, current_audio_file, is_paused, paused_audio_file

    url = context.args[0] if context.args else ""
    if not url:
        update.message.reply_text("Please provide a YouTube URL.")
        return

    update.message.reply_text(f"Downloading audio from {url}...")

    try:
        filename = download_audio(url)
        update.message.reply_text(f"Audio downloaded: {filename}")

        # Send the audio as a voice message
        with open(filename, 'rb') as audio_file:
            current_audio_file = audio_file  # Keep track of the audio file
            current_voice_message = update.message.reply_voice(audio=audio_file)

        # Optionally clean up after sending the file
        os.remove(filename)
        
        # Reset the paused state
        is_paused = False
        paused_audio_file = None
        
    except Exception as e:
        update.message.reply_text(f"Failed to download audio: {str(e)}")

# Command to pause music
def pause(update: Update, context: CallbackContext) -> None:
    global is_paused, paused_audio_file, current_voice_message

    if current_voice_message and not is_paused:
        # Pause the music by deleting the current voice message
        current_voice_message.delete()
        is_paused = True
        paused_audio_file = current_audio_file  # Store the current audio file
        update.message.reply_text("The music has been paused. Use /resume to continue playing.")
    else:
        update.message.reply_text("No music is playing or music is already paused.")

# Command to resume music
def resume(update: Update, context: CallbackContext) -> None:
    global is_paused, paused_audio_file

    if is_paused and paused_audio_file:
        is_paused = False
        update.message.reply_text("Resuming the music...")
        
        # Send the paused audio again as a new voice message
        paused_audio_file.seek(0)  # Reset the file pointer to the start
        current_voice_message = update.message.reply_voice(audio=paused_audio_file)
    else:
        update.message.reply_text("No music has been paused.")

# Command to skip music
def skip(update: Update, context: CallbackContext) -> None:
    global current_voice_message, current_audio_file

    if current_voice_message:
        # Delete the current voice message (skip the song)
        current_voice_message.delete()
        current_voice_message = None
        if current_audio_file:
            current_audio_file.close()  # Close the file
        update.message.reply_text("The music has been skipped!")

# Group Management Commands
# Command to kick a user
def kick(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        user_to_kick = update.message.reply_to_message.from_user
        update.message.chat.kick_member(user_to_kick.id)
        update.message.reply_text(f"Kicked {user_to_kick.full_name} from the group.")
    else:
        update.message.reply_text("Reply to a message to kick a user.")

# Command to ban a user
def ban(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        user_to_ban = update.message.reply_to_message.from_user
        update.message.chat.ban_member(user_to_ban.id)
        update.message.reply_text(f"Banned {user_to_ban.full_name} from the group.")
    else:
        update.message.reply_text("Reply to a message to ban a user.")

# Command to unban a user
def unban(update: Update, context: CallbackContext) -> None:
    if context.args:
        user_id = int(context.args[0])
        update.message.chat.unban_member(user_id)
        update.message.reply_text(f"Unbanned user with ID {user_id}.")
    else:
        update.message.reply_text("Please provide the user ID to unban.")

# Command to mute a user
def mute(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        user_to_mute = update.message.reply_to_message.from_user
        update.message.chat.restrict_member(user_to_mute.id, can_send_messages=False)
        update.message.reply_text(f"Muted {user_to_mute.full_name}.")
    else:
        update.message.reply_text("Reply to a message to mute a user.")

# Command to unmute a user
def unmute(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        user_to_unmute = update.message.reply_to_message.from_user
        update.message.chat.restrict_member(user_to_unmute.id, can_send_messages=True)
        update.message.reply_text(f"Unmuted {user_to_unmute.full_name}.")
    else:
        update.message.reply_text("Reply to a message to unmute a user.")

# Fun Commands
# Command to tell a joke
def joke(update: Update, context: CallbackContext) -> None:
    joke_text = random.choice(jokes)
    update.message.reply_text(joke_text)

# Command to share a random quote
def quote(update: Update, context: CallbackContext) -> None:
    quote_text = random.choice(quotes)
    update.message.reply_text(quote_text)

# Command to share a random meme
def meme(update
