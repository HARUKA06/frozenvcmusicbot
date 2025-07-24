from pyrogram import Client, filters
from pytube import YouTube
from config import API_ID, API_HASH, BOT_TOKEN
from music_queue import add_to_queue, get_next_song, get_queue, clear_queue
import os

# Initialize bot
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# This must be a user account session string, NOT a bot token.
# Use `pyrogram` to generate it. Let me know if you need help with that.
SESSION_STRING = "YOUR_USER_SESSION_STRING"

# In-memory AFK tracking
afk_users = {}

# /start
@bot.on_message(filters.command("/start	Shows welcome message
🎵 Music Commands:
• /play Play music from YouTube.
• /queue - Show current queue.
• /skip - Skip current song.
• /stop - Clear the queue.
🎤 Voice Chat Commands:
• /vplay <YouTube link> - Stream audio to group voice chat.
• /vstop - Leave voice chat.
🛌 AFK Commands:
• /afk [reason] - Set yourself as AFK.
💬 Other Commands:
• /ask <question> - Ask AI a question.
• /history - Show your last 5 questions and answers.
• /info - Show your user info.
• /id - Show chat and your user ID.
• /help - Show this message.
feedback https://t.me/JAVANON_KA_ADDA"))
async def start(client, message):
    await message.reply(
        "👋 Welcome to the Music + AFK Bot!\n"
        "Use /help to see all available commands."
    )

# /help
@bot.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
🎵 **Music Bot Commands** 🎵

**/play <YouTube link or search>**
Downloads and adds a song to the queue.

**/queue**
Show current music queue.

**/skip**
Skip the current song.

**/stop**
Stop and clear the queue.

🛌 **AFK Commands**

**/afk [reason]**
Set yourself as AFK with an optional reason.
AFK status is removed automatically when you message again.

💡 **Other**

**/start**
Start the bot and see welcome message.

**/help**
Show this help message.
"""
    await message.reply(help_text)

# /play
@bot.on_message(filters.command("play"))
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Please provide a YouTube link or search term.")
    
    query = " ".join(message.command[1:])
    
    try:
        yt = YouTube(query if query.startswith("http") else f"ytsearch:{query}")
        audio = yt.streams.filter(only_audio=True).first()
        file_path = audio.download(filename="current_song.mp3")
        add_to_queue(file_path)
        await message.reply(f"🎶 Added to queue: {yt.title}")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# /queue
@bot.on_message(filters.command("queue"))
async def queue(client, message):
    q = get_queue()
    if not q:
        await message.reply("📭 The queue is empty.")
    else:
        msg = "\n".join([f"{i+1}. {os.path.basename(song)}" for i, song in enumerate(q)])
        await message.reply(f"📜 Current Queue:\n{msg}")

# /skip
@bot.on_message(filters.command("skip"))
async def skip(client, message):
    song = get_next_song()
    if song:
        os.remove(song)
        await message.reply("⏭️ Skipped current song.")
    else:
        await message.reply("🚫 Nothing to skip.")

# /stop
@bot.on_message(filters.command("stop"))
async def stop(client, message):
    clear_queue()
    await message.reply("🛑 Queue cleared.")

# /afk
@bot.on_message(filters.command("afk"))
async def set_afk(client, message):
    user_id = message.from_user.id
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "AFK"
    afk_users[user_id] = reason
    await message.reply(f"🛌 You are now AFK: {reason}")

# Auto-remove AFK when user types
@bot.on_message(filters.private | filters.group)
async def remove_afk(client, message):
    user_id = message.from_user.id
    if user_id in afk_users:
        del afk_users[user_id]
        await message.reply("✅ Welcome back! You are no longer AFK.")

# Notify others when mentioning AFK users
@bot.on_message(filters.group)
async def notify_afk(client, message):
    if message.entities:
        for entity in message.entities:
            if entity.type in ["mention", "text_mention"]:
                user = None
                if entity.type == "mention":
                    username = message.text[entity.offset:entity.offset + entity.length]
                    try:
                        user = await client.get_users(username)
                    except:
                        pass
                elif entity.type == "text_mention":
                    user = entity.user
                if user and user.id in afk_users:
                    reason = afk_users[user.id]
                    await message.reply(f"🔕 {user.first_name} is currently AFK: {reason}")

# VPLAY command
@bot.on_message(filters.command("vplay"))
async def vplay_handler(client, message):
    chat_id = message.chat.id

    if not message.chat.type.endswith("group"):
        return await message.reply("❌ This command only works in groups.")

    if len(message.command) < 2:
        return await message.reply("❗ Provide a YouTube link.")

    url = message.text.split(None, 1)[1]
    await message.reply("⏬ Downloading audio...")

    try:
        audio_path = download_audio(url)
    except Exception as e:
        return await message.reply(f"❌ Download failed: {e}")

    await message.reply("📞 Joining voice chat...")

    try:
        await vcalls.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    audio_path,
                    HighQualityAudio()
                )
            ),
            stream_type="local_stream"
        )
        await message.reply("🎧 Streaming to voice chat!")
    except Exception as e:
        await message.reply(f"⚠️ Error joining VC: {e}")

# Leave voice chat
@bot.on_message(filters.command("vstop"))
async def vstop_handler(client, message):
    try:
        await vcalls.leave_group_call(message.chat.id)
        await message.reply("🛑 Left voice chat.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# Start everything
async def main():
    await user.start()
    await bot.start()
    await vcalls.start()
    print("🤖 VPlay bot is running...")
    await idle()
    await user.stop()
    await bot.stop()

@bot.on_message(filters.command("ask"))
async def ask_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❓ Please ask a full question.\nUsage: `/ask What is Python?`", quote=True)

    question = " ".join(message.command[1:])
    
    # === Placeholder answer ===
    # You can integrate real AI later (see below)
    if "capital of france" in question.lower():
        answer = "🧠 Paris is the capital of France."
    elif "who is elon musk" in question.lower():
        answer = "🧠 Elon Musk is the CEO of Tesla and SpaceX."
    else:
        answer = "🤖 I'm just a simple bot. I don't know that yet!"

    await message.reply(answer, quote=True)

# Dictionary to store user question history for /ask
user_history = {}

# /info command — user info
@bot.on_message(filters.command("info"))
async def info(client, message):
    user = message.from_user
    text = f"""
👤 User Info:
• Name: {user.first_name} {user.last_name or ""}
• Username: @{user.username or "N/A"}
• User ID: {user.id}
• Language Code: {user.language_code or "N/A"}
"""
    await message.reply(text.strip())

# /id command — chat & user IDs
@bot.on_message(filters.command("id"))
async def show_id(client, message):
    chat = message.chat
    user = message.from_user
    text = f"""
🆔 IDs:
• Chat ID: {chat.id}
• Chat Type: {chat.type}
• Your User ID: {user.id}
"""
    await message.reply(text.strip())

# Updated /ask command to save history
@bot.on_message(filters.command("ask"))
async def ask(client, message):
    if len(message.command) < 2:
        return await message.reply("❓ Usage: /ask <your question>")

    question = " ".join(message.command[1:])
    await message.reply("🤖 Thinking...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            max_tokens=150,
        )
        answer = response.choices[0].message.content.strip()

        # Save question and answer in user history
        user_id = message.from_user.id
        if user_id not in user_history:
            user_history[user_id] = []
        user_history[user_id].append({"question": question, "answer": answer})

        await message.reply(f"🧠 {answer}")
    except Exception as e:
        await message.reply(f"⚠️ OpenAI error: {e}")

# /history command — show user's ask history
@bot.on_message(filters.command("history"))
async def history(client, message):
    user_id = message.from_user.id
    history = user_history.get(user_id)

    if not history:
        return await message.reply("📭 You have no history yet.")

    # Show last 5 Q&A to avoid flooding
    last_five = history[-5:]
    text = "🕑 Your last questions and answers:\n\n"
    for i, entry in enumerate(last_five, 1):
        text += f"{i}. Q: {entry['question']}\n   A: {entry['answer']}\n\n"

    await message.reply(text.strip())


if __name__ == "__main__":
    asyncio.run(main())
# Run the bot
