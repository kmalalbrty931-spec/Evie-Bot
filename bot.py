import re
import random
import os
import threading
from flask import Flask
from collections import defaultdict, deque
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- نظام السيرفر الوهمي لإبقاء البوت حياً على Render ---
app = Flask('')
@app.route('/')
def home(): return "Evie Queen is Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- إعدادات البوت والتوكن ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_NAMES = ["ايفي", "إيفي", "evie", "Evie"]

# ذاكرة بسيطة وردود ساخرة
chat_memory = defaultdict(lambda: deque(maxlen=40))
sarcastic_replies = [
    "واو... نكتة القرن، باقي يصفق لك مين؟ 😏",
    "خف علينا يا كوميدي زمانك 😂",
    "واضح انك تعبت على هالنكتة... بدون نتيجة.",
    "لو السكوت ذهب، أنت خسران كثير.",
    "تراك متحمس زيادة عن اللزوم.",
    "واضح المزح عندك يحتاج تحديث."
]

called_replies = [
    "هلا؟ ناديتني ولا مشتاق لصوتي؟ 😏",
    "جيت، تكلم بسرعة وقتي ثمين.",
    "وش تبي؟ اختصر ولا أطنش.",
    "نعم؟ إذا موضوع تافه انسحب من الآن."
]

# --- وظائف المعالجة ---
def get_user(user):
    return "@" + user.username if user.username else (user.first_name or "يا أنت")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip().lower()
    user_name = get_user(update.message.from_user)

    # إذا ناداها أحد
    if any(name.lower() in text for name in BOT_NAMES):
        if any(w in text for w in ["احب", "عسل", "جميلة"]):
            await update.message.reply_text(f"خف علينا يا {user_name}، لا تتعلق بسرعة 😌")
        elif any(w in text for w in ["نكتة", "مزح", "غبية"]):
            await update.message.reply_text(random.choice(sarcastic_replies))
        else:
            await update.message.reply_text(random.choice(called_replies))

# --- تشغيل البوت ---
def main():
    keep_alive() # تشغيل السيرفر الوهمي أولاً
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    print("Evie is running with keep-alive server...")
    app_tg.run_polling()

if __name__ == "__main__":
    main()
