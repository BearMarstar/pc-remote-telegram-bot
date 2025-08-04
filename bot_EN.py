import telebot
from telebot import types
import os
import socket
import pyautogui
import platform
import sys
import subprocess
import time

TOKEN = 'YOUR_TOKEN_HERE'
AUTHORIZED_USERS = {123456789}  # Replace with your Telegram ID

bot = telebot.TeleBot(TOKEN)

# Media control imports
if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
elif platform.system() == "Darwin":  # macOS
    from AppKit import NSSound
    import applescript

def is_authorized(message):
    return message.from_user.id in AUTHORIZED_USERS

def escape_md(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return ''.join(['\\' + char if char in escape_chars else char for char in str(text)])

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Unable to get IP"

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        types.KeyboardButton("📟 Ping"),
        types.KeyboardButton("📸 Screenshot"),
        types.KeyboardButton("🖥️ Local IP"),
        types.KeyboardButton("⏻ Shutdown PC"),
        types.KeyboardButton("🔄 Restart PC"),
        types.KeyboardButton("ℹ️ System Info"),
        types.KeyboardButton("⏯️ Play/Pause"),
        types.KeyboardButton("⏭️ Next Track"),
        types.KeyboardButton("⏮️ Previous Track"),
        types.KeyboardButton("🔈 Volume Down"),
        types.KeyboardButton("🔉 Volume Up"),
        types.KeyboardButton("🔇 Mute")
    ]
    keyboard.add(*buttons[:6])
    keyboard.add(*buttons[6:9])
    keyboard.add(*buttons[9:])
    return keyboard

# Media control functions (windows/macOS/linux) same as before...

# Authorization and command handlers with English messages:

@bot.message_handler(commands=['start'])
def cmd_start(message):
    if is_authorized(message):
        bot.send_message(
            message.chat.id,
            "🎵 PC control activated!\nSelect an action:",
            reply_markup=main_keyboard()
        )
    else:
        bot.reply_to(
            message,
            f"🚫 Access denied! \nYour ID: {message.from_user.id}"
        )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if not is_authorized(message):
        bot.reply_to(message, "🚫 Unauthorized access!")
        return

    text = message.text

    if text == "📟 Ping":
        bot.reply_to(message, "✅ PC is running normally")

    elif text == "📸 Screenshot":
        try:
            path = "screenshot.png"
            pyautogui.screenshot(path)
            with open(path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove(path)
        except Exception as e:
            bot.reply_to(message, f"❌ Screenshot error: {str(e)}")

    elif text == "🖥️ Local IP":
        ip = escape_md(get_local_ip())
        bot.reply_to(message, f"🌐 *Local IP:* `{ip}`", parse_mode='MarkdownV2')

    elif text == "⏻ Shutdown PC":
        bot.reply_to(message, "⚠️ The PC will shutdown in 5 seconds!")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")

    elif text == "🔄 Restart PC":
        bot.reply_to(message, "🔄 Restarting in 5 seconds...")
        if platform.system() == "Windows":
            os.system("shutdown /r /t 5")
        else:
            os.system("shutdown -r now")
    
    elif text == "ℹ️ System Info":
        system_info = (
            f"*OS:* {escape_md(platform.system())}\n"
            f"*Version:* {escape_md(platform.version())}\n"
            f"*Processor:* {escape_md(platform.processor())}\n"
            f"*User:* {escape_md(os.getlogin())}"
        )
        bot.reply_to(message, system_info, parse_mode='MarkdownV2')
    
    # Media controls
    elif text == "⏯️ Play/Pause":
        if media_control("playpause"):
            bot.reply_to(message, "⏯️ Playback toggled")
        else:
            bot.reply_to(message, "❌ Media control error")
    
    elif text == "⏭️ Next Track":
        if media_control("next"):
            bot.reply_to(message, "⏭️ Next track")
        else:
            bot.reply_to(message, "❌ Media control error")
    
    elif text == "⏮️ Previous Track":
        if media_control("prev"):
            bot.reply_to(message, "⏮️ Previous track")
        else:
            bot.reply_to(message, "❌ Media control error")
    
    elif text == "🔉 Volume Up":
        if media_control("volup"):
            bot.reply_to(message, "🔉 Volume increased")
        else:
            bot.reply_to(message, "❌ Volume control error")
    
    elif text == "🔈 Volume Down":
        if media_control("voldown"):
            bot.reply_to(message, "🔈 Volume decreased")
        else:
            bot.reply_to(message, "❌ Volume control error")
    
    elif text == "🔇 Mute":
        if media_control("mute"):
            bot.reply_to(message, "🔇 Sound muted")
        else:
            bot.reply_to(message, "❌ Mute error")

    else:
        bot.reply_to(message, "❌ Unknown command")

@bot.message_handler(commands=['user_id'])
def cmd_user_id(message):
    user_id = escape_md(message.from_user.id)
    bot.reply_to(message, f"👤 Your Telegram ID: `{user_id}`", parse_mode='MarkdownV2')

@bot.message_handler(commands=['help'])
def cmd_help(message):
    help_text = (
        "🎵 Media control:\n"
        "• ⏯️ Play/Pause - Toggle playback\n"
        "• ⏭️ Next Track - Next song\n"
        "• ⏮️ Previous Track - Previous song\n"
        "• 🔈 Volume Down - Decrease volume\n"
        "• 🔉 Volume Up - Increase volume\n"
        "• 🔇 Mute - Mute sound\n\n"
        "💻 System commands:\n"
        "• 📟 Ping - Check PC status\n"
        "• 📸 Screenshot - Get a screen capture\n"
        "• 🖥️ Local IP - Get local IP address\n"
        "• ℹ️ System Info - Show system info\n"
        "• ⏻ Shutdown PC - Shutdown the computer\n"
        "• 🔄 Restart PC - Restart the computer"
    )
    bot.send_message(message.chat.id, help_text)

if __name__ == '__main__':
    print("Bot started...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
