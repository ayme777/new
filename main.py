import telebot
from telebot import types
from flask import Flask, request
import threading
from config import TOKEN
import ssl  # Ensure the SSL module is imported

# Initialize the bot and Flask app
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

questions = {
    '1': "ما هي عاصمة فلسطين؟",
    '2': "ما هو عدد الكواكب في المجموعة الشمسية؟",
    '3': "من هو مخترع المصباح الكهربائي؟",
    '4': "كم عدد ألوان قوس قزح؟",
    '5': "ما هو أكبر محيط على الأرض؟"
}

options = {
    '1': [("رام الله", '0'), ("القدس", '1'), ("نابلس", '0')],
    '2': [("8", '0'), ("9", '1'), ("10", '0')],
    '3': [("توماس إديسون", '1'), ("ألكسندر غراهام بيل", '0'), ("نيكولا تسلا", '0')],
    '4': [("5", '0'), ("7", '1'), ("6", '0')],
    '5': [("المحيط الهندي", '0'), ("المحيط الأطلسي", '0'), ("المحيط الهادئ", '1')]
}

points = {}

CHANNEL_USERNAME = "@iptvipfree"

def create_inline_keyboard(question_id):
    """Creates an inline keyboard for a specific question."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for text, call_data in options[question_id]:
        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"{question_id}_{call_data}"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    """Sends a welcome message and starts the quiz."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user already has points, otherwise initialize
    if user_id not in points:
        points[user_id] = 0

    # Create buttons for subscription check
    markup = types.InlineKeyboardMarkup(row_width=1)
    check_btn = types.InlineKeyboardButton(text="تحقق من الاشتراك", callback_data="check_subscription")
    markup.add(check_btn)

    bot.send_message(
        chat_id,
        f"مرحبا بك في مسابقة المعلومات العامة! \nID حسابك هو: {user_id} \nنقاطك الحالية: {points[user_id]} \nاضغط على الزر أدناه للتحقق من الاشتراك في القناة أولاً: https://t.me/iptvipfree",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    """Handles user interaction with inline buttons."""
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "check_subscription":
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                markup = types.InlineKeyboardMarkup(row_width=1)
                start_quiz_btn = types.InlineKeyboardButton(text="ابدأ مسابقة عمر التثقيفية!", callback_data="start_quiz")
                markup.add(start_quiz_btn)

                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=f"تم التحقق بنجاح! يمكنك الآن بدء المسابقة. \nID حسابك هو: {user_id} \nعدد نقاطك الحالية: {points[user_id]} \nاضغط على الزر أدناه لبدء المسابقة:",
                    reply_markup=markup
                )
            else:
                bot.answer_callback_query(call.id, text="عذراً، لم يتم العثور على اشتراكك في القناة.")
        except Exception:
            bot.answer_callback_query(call.id, text="حدث خطأ أثناء التحقق من الاشتراك.")

    elif call.data == "start_quiz":
        bot.answer_callback_query(call.id, text="لنبدأ المسابقة!")
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=questions['1'],
            reply_markup=create_inline_keyboard('1')
        )
    elif "_" in call.data:
        process_answer(call, user_id)

def process_answer(call, user_id):
    """Processes the user's answer and sends feedback."""
    question_id, answer = call.data.split("_")
    question_id = str(question_id)
    correct_answer = next(opt for opt in options[question_id] if opt[1] == '1')[0]

    if answer == '1':
        points[user_id] += 1
        bot.answer_callback_query(call.id, text="إجابة صحيحة!")
    else:
        bot.answer_callback_query(call.id, text=f"إجابة خاطئة! الإجابة الصحيحة هي: {correct_answer}")

    # Send the next question or end the quiz
    next_question_id = str(int(question_id) + 1)
    if next_question_id in questions:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=questions[next_question_id],
            reply_markup=create_inline_keyboard(next_question_id)
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"انتهت المسابقة! عدد نقاطك الإجمالي هو: {points[user_id]}."
        )

# Flask route for UptimeRobot
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Run the bot
if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    try:
        bot.polling(non_stop=True)
    except Exception as ex:
        print(f"An error occurred: {ex}")
