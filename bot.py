import telebot
from telebot import types
import os
import platform
import pyautogui
import socket

TOKEN = 'ТВОЙ_ТОКЕН_ЗДЕСЬ'
AUTHORIZED_USERS = {123456789}  # Замените на свой Telegram ID

bot = telebot.TeleBot(TOKEN)

def is_authorized(message):
    return message.from_user.id in AUTHORIZED_USERS

def escape_md(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return ''.join(['\\' + c if c in escape_chars else c for c in str(text)])

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Не удалось определить IP"

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        types.KeyboardButton("📟 Проверка связи"),
        types.KeyboardButton("📸 Скриншот"),
        types.KeyboardButton("🖥️ Локальный IP"),
        types.KeyboardButton("⏻ Выключить ПК"),
        types.KeyboardButton("⏳ Таймер выключения"),
        types.KeyboardButton("🔄 Перезагрузить ПК"),
        types.KeyboardButton("ℹ️ Информация о системе"),
        # Кнопки управления музыкой
        types.KeyboardButton("⏯️ Плей/Пауза"),
        types.KeyboardButton("⏭️ Следующий трек"),
        types.KeyboardButton("⏮️ Предыдущий трек"),
        types.KeyboardButton("🔉 Громкость +"),
        types.KeyboardButton("🔈 Громкость -"),
        types.KeyboardButton("🔇 Выключить звук"),
    ]
    keyboard.add(*buttons)
    return keyboard

def timer_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(types.KeyboardButton("Отмена"))
    return keyboard

# Функция для управления музыкой с pyautogui (пример для Windows)
def media_control(action):
    try:
        # Варианты для pyautogui:
        # playpause: 'playpause' или 'space' (зависит от плеера)
        # next: 'nexttrack'
        # prev: 'prevtrack'
        # volumeup/volumedown/mute могут требовать реализации через system calls
        if action == "playpause":
            pyautogui.press('playpause')
        elif action == "next":
            pyautogui.press('nexttrack')
        elif action == "prev":
            pyautogui.press('prevtrack')
        elif action == "volup":
            pyautogui.press('volumeup')
        elif action == "voldown":
            pyautogui.press('volumedown')
        elif action == "mute":
            pyautogui.press('volumemute')
        else:
            return False
        return True
    except Exception as e:
        print(f"Media control error: {e}")
        return False

@bot.message_handler(commands=['start'])
def cmd_start(message):
    if is_authorized(message):
        bot.send_message(message.chat.id, "Привет! Выбери действие:", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, f"🚫 Доступ запрещён! Ваш ID: {message.from_user.id}")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    if not is_authorized(message):
        bot.reply_to(message, "🚫 Неавторизованный доступ!")
        return

    text = message.text

    if text == "📟 Проверка связи":
        bot.reply_to(message, "✅ ПК работает в штатном режиме")

    elif text == "📸 Скриншот":
        try:
            path = "screenshot.png"
            pyautogui.screenshot(path)
            with open(path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove(path)
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка создания скриншота: {e}")

    elif text == "🖥️ Локальный IP":
        ip = escape_md(get_local_ip())
        bot.reply_to(message, f"🌐 Локальный IP: `{ip}`", parse_mode='MarkdownV2')

    elif text == "⏻ Выключить ПК":
        bot.reply_to(message, "⚠️ Компьютер будет выключен через 5 секунд!")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")

    elif text == "🔄 Перезагрузить ПК":
        bot.reply_to(message, "🔄 Перезагрузка через 5 секунд...")
        if platform.system() == "Windows":
            os.system("shutdown /r /t 5")
        else:
            os.system("shutdown -r now")

    elif text == "ℹ️ Информация о системе":
        info = (
            f"*ОС:* {escape_md(platform.system())}\n"
            f"*Версия:* {escape_md(platform.version())}\n"
            f"*Процессор:* {escape_md(platform.processor())}\n"
            f"*Пользователь:* {escape_md(os.getlogin())}"
        )
        bot.reply_to(message, info, parse_mode='MarkdownV2')

    # Управление музыкой
    elif text == "⏯️ Плей/Пауза":
        if media_control("playpause"):
            bot.reply_to(message, "⏯️ Плей/Пауза")
        else:
            bot.reply_to(message, "❌ Ошибка управления музыкой")

    elif text == "⏭️ Следующий трек":
        if media_control("next"):
            bot.reply_to(message, "⏭️ Следующий трек")
        else:
            bot.reply_to(message, "❌ Ошибка управления музыкой")

    elif text == "⏮️ Предыдущий трек":
        if media_control("prev"):
            bot.reply_to(message, "⏮️ Предыдущий трек")
        else:
            bot.reply_to(message, "❌ Ошибка управления музыкой")

    elif text == "🔉 Громкость +":
        if media_control("volup"):
            bot.reply_to(message, "🔉 Громкость увеличена")
        else:
            bot.reply_to(message, "❌ Ошибка управления громкостью")

    elif text == "🔈 Громкость -":
        if media_control("voldown"):
            bot.reply_to(message, "🔈 Громкость уменьшена")
        else:
            bot.reply_to(message, "❌ Ошибка управления громкостью")

    elif text == "🔇 Выключить звук":
        if media_control("mute"):
            bot.reply_to(message, "🔇 Звук отключен")
        else:
            bot.reply_to(message, "❌ Ошибка отключения звука")

    elif text == "⏳ Таймер выключения":
        msg = bot.send_message(message.chat.id, "Через сколько минут выключить ПК? Введи число:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("Отмена")))
        bot.register_next_step_handler(msg, set_timer)

    elif text == "Отмена":
        if platform.system() == "Windows":
            os.system("shutdown /a")
            bot.send_message(message.chat.id, "⛔ Таймер выключения отменён.", reply_markup=main_keyboard())
        else:
            bot.send_message(message.chat.id, "Отмена таймера для этой ОС не реализована.", reply_markup=main_keyboard())

    else:
        bot.reply_to(message, "❌ Неизвестная команда")

def set_timer(message):
    if message.text.lower() == "отмена":
        if platform.system() == "Windows":
            os.system("shutdown /a")
            bot.send_message(message.chat.id, "⛔ Таймер выключения отменён.", reply_markup=main_keyboard())
        else:
            bot.send_message(message.chat.id, "Отмена таймера для этой ОС не реализована.", reply_markup=main_keyboard())
        return

    if message.text.isdigit():
        minutes = int(message.text)
        if minutes <= 0:
            bot.reply_to(message, "Введите число больше нуля.")
            return
        bot.send_message(message.chat.id, f"Компьютер будет выключен через {minutes} минут.", reply_markup=main_keyboard())
        if platform.system() == "Windows":
            os.system(f"shutdown /s /t {minutes * 60}")
        else:
            os.system(f"bash -c 'sleep {minutes * 60} && shutdown -h now' &")
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите число минут или 'Отмена'.")
        bot.register_next_step_handler(msg, set_timer)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
