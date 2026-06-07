import os
import telebot
import anthropic
import random

# === SHU YERGA O'Z MA'LUMOTLARINGIZNI KIRITING ===
TELEGRAM_TOKEN = "8631661002:AAEyglH-bC0U-48eV6rs-0iRhDiG5Jqrv-I"  # BotFather tokeni
CLAUDE_API_KEY = "sk-ant-..."  # O'zingizning Claude API key

# =============================================

bot = telebot.TeleBot(TELEGRAM_TOKEN)
claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

user_scores = {}

def ask_claude(prompt):
    message = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_scores[user_id] = 0
    bot.send_message(user_id, 
        "🇹🇷 Turk tili Quiz Botiga xush kelibsiz!\n\n"
        "📚 Men sizga turk tili so'zlari va qoidalaridan savollar beraman.\n\n"
        "Buyruqlar:\n"
        "/quiz - Yangi savol\n"
        "/lugat - So'z o'rganish\n"
        "/qoida - Grammatika qoidasi\n"
        "/ball - Ballingiz\n"
        "/start - Qayta boshlash"
    )

@bot.message_handler(commands=['quiz'])
def quiz(message):
    user_id = message.chat.id
    bot.send_message(user_id, "⏳ Savol tayyorlanmoqda...")
    
    quiz_types = [
        "Turk tilidan o'zbekchaga tarjima qilish",
        "O'zbekchadan turk tiliga tarjima qilish", 
        "Turk tilida so'zning sinonimi",
        "Turk tilida gap to'ldirish"
    ]
    quiz_type = random.choice(quiz_types)
    
    prompt = f"""Turk tili o'rganuvchilar uchun {quiz_type} bo'yicha bitta test savol yarat.

Format qat'iy shu ko'rinishda bo'lsin:

SAVOL: [savol matni]
A) [variant]
B) [variant]  
C) [variant]
D) [variant]
TO'G'RI JAVOB: [faqat harf, masalan: A]
IZOH: [qisqacha izoh o'zbek tilida]

Faqat shu formatda yoz, boshqa hech narsa qo'shma."""

    response = ask_claude(prompt)
    
    lines = response.strip().split('\n')
    correct_answer = ""
    for line in lines:
        if line.startswith("TO'G'RI JAVOB:"):
            correct_answer = line.replace("TO'G'RI JAVOB:", "").strip()
            break
    
    # Savolni foydalanuvchiga yuborish
    question_text = ""
    for line in lines:
        if not line.startswith("TO'G'RI JAVOB:") and not line.startswith("IZOH:"):
            question_text += line + "\n"
    
    explanation = ""
    for line in lines:
        if line.startswith("IZOH:"):
            explanation = line.replace("IZOH:", "").strip()
    
    # Javob tugmalarini yaratish
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("A", callback_data=f"ans_A_{correct_answer}_{explanation[:50]}"),
        telebot.types.InlineKeyboardButton("B", callback_data=f"ans_B_{correct_answer}_{explanation[:50]}"),
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("C", callback_data=f"ans_C_{correct_answer}_{explanation[:50]}"),
        telebot.types.InlineKeyboardButton("D", callback_data=f"ans_D_{correct_answer}_{explanation[:50]}"),
    )
    
    bot.send_message(user_id, question_text.strip(), reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ans_"))
def check_answer(call):
    user_id = call.message.chat.id
    parts = call.data.split("_", 3)
    user_choice = parts[1]
    correct = parts[2]
    explanation = parts[3] if len(parts) > 3 else ""
    
    if user_id not in user_scores:
        user_scores[user_id] = 0
    
    if user_choice == correct:
        user_scores[user_id] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri!")
        bot.send_message(user_id, 
            f"✅ *To'g'ri javob!* +1 ball\n"
            f"💡 {explanation}\n\n"
            f"🏆 Ballingiz: {user_scores[user_id]}\n\n"
            f"Davom etish uchun /quiz",
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Noto'g'ri!")
        bot.send_message(user_id,
            f"❌ *Noto'g'ri!* To'g'ri javob: *{correct}*\n"
            f"💡 {explanation}\n\n"
            f"🏆 Ballingiz: {user_scores[user_id]}\n\n"
            f"Davom etish uchun /quiz",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['lugat'])
def lugat(message):
    user_id = message.chat.id
    bot.send_message(user_id, "⏳ So'z tayyorlanmoqda...")
    
    prompt = """Turk tilidan bitta foydali so'z o'rgatuvchi karta yarat.

Format:
🇹🇷 So'z: [turk tilida]
🇺🇿 Tarjima: [o'zbek tilida]
🔊 Talaffuz: [qanday o'qiladi]
📝 Misol: [turk tilida gap]
🇺🇿 Misol tarjimasi: [o'zbek tilida]

Kundalik hayotda ko'p ishlatiladigan so'zlardan tanlang."""

    response = ask_claude(prompt)
    bot.send_message(user_id, response)

@bot.message_handler(commands=['qoida'])
def qoida(message):
    user_id = message.chat.id
    bot.send_message(user_id, "⏳ Qoida tayyorlanmoqda...")
    
    prompt = """Turk tili grammatikasidan bitta muhim qoidani o'zbek tilida tushuntir.

Format:
📌 QOIDA: [qoida nomi]
📖 Tushuntirish: [oddiy tilda izoh]
✅ Misol 1: [turk tilida] = [o'zbek tilida]
✅ Misol 2: [turk tilida] = [o'zbek tilida]
⚠️ Eslatma: [muhim nuqta]

Boshlang'ich darajadagi o'rganuvchilar uchun mos qoida tanlang."""

    response = ask_claude(prompt)
    bot.send_message(user_id, response)

@bot.message_handler(commands=['ball'])
def ball(message):
    user_id = message.chat.id
    score = user_scores.get(user_id, 0)
    
    if score == 0:
        emoji = "🌱"
        daraja = "Yangi boshlovchi"
    elif score < 5:
        emoji = "📚"
        daraja = "O'rganuvchi"
    elif score < 15:
        emoji = "⭐"
        daraja = "Yaxshi"
    elif score < 30:
        emoji = "🌟"
        daraja = "A'lo"
    else:
        emoji = "🏆"
        daraja = "Ustoz"
    
    bot.send_message(user_id,
        f"{emoji} *Sizning natijangiz*\n\n"
        f"🏆 Ball: *{score}*\n"
        f"📊 Daraja: *{daraja}*\n\n"
        f"Davom eting! /quiz",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def default(message):
    bot.send_message(message.chat.id,
        "Buyruqlardan foydalaning:\n"
        "/quiz - Test savol\n"
        "/lugat - Yangi so'z\n"
        "/qoida - Grammatika\n"
        "/ball - Ballingiz"
    )

print("✅ Bot ishga tushdi!")
bot.polling(none_stop=True)
