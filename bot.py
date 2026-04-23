# EvieQueenBot - نسخة Render المعدلة (Web Service + Bot)
# pip install python-telegram-bot==20.7 flask

import re
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# ضع التوكن هنا
# =========================
TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

BOT_NAMES = ["ايفي", "إيفي", "evie", "Evie"]

# =========================
# Flask Web Server لخداع Render
# =========================
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Evie is alive 😏"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

# =========================
# كلمات ممنوعة وروابط
# =========================
BAD_WORDS = ["سب", "قذف", "كلب", "حمار", "حقير"]
LINKS = ["http://", "https://", "t.me/", "www."]

# =========================
# ردود
# =========================
sarcastic = [
    "واو... نكتة قوية، باقي أحد يضحك بس 😏",
    "خف علينا يا نجم الكوميديا.",
    "أنا احترمت المحاولة فقط.",
    "واضح المزح عندك يحتاج صيانة 😂",
    "تكلم أكثر... أبي أضحك على الثقة.",
]

called = [
    "هلا؟ ناديتني؟ تكلم بسرعة.",
    "جيت، وش عندك؟",
    "أنا هنا، القروب صار أجمل الآن.",
    "نعم؟ إذا موضوع سخيف انسحب.",
]

jealous = [
    "تمدح غيري وأنا موجودة؟ جرأة 🙄",
    "واضح نسيت مين النجمة هنا.",
    "حلو... وأنا مجرد أسطورة جانبية؟",
]

# =========================
# أدوات
# =========================
def has_link(text):
    t = text.lower()
    return any(x in t for x in LINKS)

def has_bad(text):
    t = text.lower()
    return any(x in t for x in BAD_WORDS)

def called_evie(text):
    t = text.lower()
    return any(x.lower() in t for x in BOT_NAMES)

# =========================
# البوت
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.message.from_user.first_name

    # حذف الروابط
    if has_link(text):
        try:
            await update.message.delete()
            await update.message.reply_text(
                "تم حذف الرابط، مو فاتحين سوق هنا 😌"
            )
        except:
            pass
        return

    # حذف الإساءة
    if has_bad(text):
        try:
            await update.message.delete()
            await update.message.reply_text(
                "تم حذف الرسالة، ارفع مستوى الكلام."
            )
        except:
            pass
        return

    # إذا رد على رسالة البوت
    if update.message.reply_to_message:
        if update.message.reply_to_message.from_user.is_bot:
            await update.message.reply_text(
                random.choice(sarcastic)
            )
            return

    # إذا ناداها
    if called_evie(text):

        if "احب" in text and "ايفي" not in text.lower():
            await update.message.reply_text(
                random.choice(jealous)
            )
            return

        if "مزح" in text or "غبية" in text:
            await update.message.reply_text(
                random.choice(sarcastic)
            )
            return

        await update.message.reply_text(
            random.choice(called)
        )

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle)
    )

    print("Evie Bot Running...")
    app.run_polling()

# =========================
# تشغيل الاثنين معاً
# =========================
if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t1.start()

    run_web()
