import os
import threading
import random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- السيرفر الوهمي (لازم يكون موجود عشان Render) ---
app = Flask('')
@app.route('/')
def home(): return "Evie is Alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- إعدادات البوت ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
BOT_NAMES = ["ايفي", "إيفي", "evie"]

sarcastic_replies = [
    "واو... نكتة القرن، باقي يصفق لك مين؟ 😏",
    "خف علينا يا كوميدي زمانك 😂",
    "لو السكوت ذهب، أنت خسران كثير.",
    "تراك متحمس زيادة عن اللزوم.",
    "هلا؟ ناديتني ولا مشتاق لصوتي؟ 😏"
]

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    # إذا ناديت اسمها
    if any(name in text for name in BOT_NAMES):
        await update.message.reply_text(random.choice(sarcastic_replies))

def main():
    keep_alive() # تشغيل السيرفر
    if not TOKEN:
        print("Error: No TELEGRAM_TOKEN found!")
        return
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    print("Evie Bot Started...")
    application.run_polling()

if __name__ == "__main__":
    main()
