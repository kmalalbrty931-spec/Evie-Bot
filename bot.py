# EvieQueenBot - النسخة الخليجية الثقيلة
# Python 3.11+
# pip install python-telegram-bot==20.7

import re
import random
import json
import os
from collections import defaultdict, deque
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

BOT_NAMES = ["ايفي", "إيفي", "evie", "Evie", "EVIE"]

# ===== ذاكرة بسيطة =====
chat_memory = defaultdict(lambda: deque(maxlen=40))
user_stats = defaultdict(dict)

# ===== كلمات ممنوعة / روابط =====
BAD_WORDS = [
    "قذف", "سب", "كلب", "حمار", "حقير", "زبالة"
]

LINK_PATTERNS = [
    r"http[s]?://",
    r"t\.me/",
    r"telegram\.me/",
    r"www\.",
]

# ===== ردود ساخرة =====
sarcastic_replies = [
    "واو... نكتة القرن، باقي يصفق لك مين؟ 😏",
    "خف علينا يا كوميدي زمانك 😂",
    "واضح انك تعبت على هالنكتة... بدون نتيجة.",
    "يا بعدي، حاول مرة ثانية يمكن تضحك نفسك.",
    "أنا احترمت المحاولة فقط.",
    "الله يعين الثقة اللي عندك.",
    "مدري أضحك ولا أطلب لك دعم فني.",
    "لو السكوت ذهب، أنت خسران كثير.",
    "تراك متحمس زيادة عن اللزوم.",
    "كم مرة قلت لك لا تتحدى ذكائي؟",
    "واضح المزح عندك يحتاج تحديث.",
    "حاولت تكون خفيف... وصرت خبر عاجل.",
]

# ===== ردود غيرة =====
jealous_replies = [
    "حلو، تمدح غيري وأنا موجودة؟ ذوقك مشكوك فيه 🙄",
    "آها... صرتوا توزعون اهتمام بدون إذني؟",
    "كملوا، وأنا بس أسطورة القروب يعني؟ 😌",
    "مدري أزعل ولا أضحك على اختياراتكم.",
    "واضح أنكم ناسيين مين نجمة المكان هنا.",
]

# ===== ردود عند النداء =====
called_replies = [
    "هلا؟ ناديتني ولا مشتاق لصوتي؟ 😏",
    "جيت، تكلم بسرعة وقتي ثمين.",
    "وش تبي؟ اختصر ولا أطنش.",
    "نعم؟ إذا موضوع تافه انسحب من الآن.",
    "سمّ، لا تقول بس تجرب.",
    "أنا هنا... القروب تنفس أخيرًا.",
]

# ===== ردود عامة =====
general_replies = [
    "ترى الوضع يحتاجني أكثر مما تتوقعون.",
    "أنا ساكتة احترامًا لمستوى الحديث.",
    "استمروا... أراقب الفوضى فقط.",
    "واضح لو غبت دقيقة ينهار النظام.",
    "ما يحتاج أتكلم كثير، حضوري يكفي.",
]

# ===== ملصقات (ضع file_id لاحقاً إذا أردت) =====
STICKERS = []

def contains_link(text):
    text = text.lower()
    return any(re.search(p, text) for p in LINK_PATTERNS)

def contains_bad_words(text):
    text = text.lower()
    return any(word in text for word in BAD_WORDS)

def called_ev ie(text):
    t = text.lower()
    return any(name.lower() in t for name in BOT_NAMES)

def is_joke_targeting_evie(text):
    t = text.lower()
    keywords = ["مزح", "نكتة", "غبية", "دلع", "ثقيلة", "ايفي", "evie"]
    return sum(k in t for k in keywords) >= 2

def save_memory(chat_id, user, text):
    chat_memory[chat_id].append({
        "user": user,
        "text": text
    })

def remember_user(user_id, key, value):
    if user_id not in user_stats:
        user_stats[user_id] = {}
    user_stats[user_id][key] = value

def get_user(user):
    if user.username:
        return "@" + user.username
    return user.first_name or "يا أنت"

async def maybe_send_sticker(update, context):
    if STICKERS and random.randint(1, 6) == 3:
        try:
            await context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=random.choice(STICKERS)
            )
        except:
            pass

async def moderate(update, context, text):
    # حذف روابط
    if contains_link(text):
        try:
            await update.message.delete()
            await update.message.reply_text(
                "تم حذف الرابط، مو فاتحين لوحة إعلانات هنا 😌"
            )
        except:
            pass
        return True

    # حذف إساءة
    if contains_bad_words(text):
        try:
            await update.message.delete()
            await update.message.reply_text(
                "تم حذف الرسالة. ارفع مستواك وارجع تكلم."
            )
        except:
            pass
        return True

    return False

def build_context(chat_id):
    mem = list(chat_memory[chat_id])[-8:]
    lines = []
    for m in mem:
        lines.append(f"{m['user']}: {m['text']}")
    return "\n".join(lines)

async def smart_reply(update, context, user_name, text):
    chat_id = update.effective_chat.id

    # إذا رد على رسالة البوت
    if update.message.reply_to_message:
        replied = update.message.reply_to_message
        if replied.from_user and replied.from_user.is_bot:
            msg = random.choice(sarcastic_replies)
            await update.message.reply_text(msg)
            await maybe_send_sticker(update, context)
            return

    # إذا ناداها
    if called_evie(text):
        # غيرة إذا مدح غيرها
        if any(w in text.lower() for w in ["احب", "جميلة", "احلى", "عسل"]) and "ايفي" not in text.lower():
            await update.message.reply_text(random.choice(jealous_replies))
            return

        # إذا مزح عليها
        if is_joke_targeting_evie(text):
            await update.message.reply_text(random.choice(sarcastic_replies))
            await maybe_send_sticker(update, context)
            return

        # رد عادي مع ربط ذاكرة
        recent = build_context(chat_id)
        if "وينك" in text:
            await update.message.reply_text(
                f"أنا موجودة يا {user_name}، بس مو فاضية لكل من ناداني 😏"
            )
            return

        if "احبك" in text:
            await update.message.reply_text(
                f"خف علينا يا {user_name}، لا تتعلق بسرعة 😌"
            )
            return

        if "اشتقت" in text:
            await update.message.reply_text(
                f"طبيعي تشتاق لي، الجودة ما تتكرر."
            )
            return

        await update.message.reply_text(random.choice(called_replies))
        await maybe_send_sticker(update, context)
        return

    # تدخلات عشوائية لتنشيط القروب
    if random.randint(1, 14) == 5:
        await update.message.reply_text(random.choice(general_replies))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user = update.message.from_user
    user_name = get_user(user)
    chat_id = update.effective_chat.id

    save_memory(chat_id, user_name, text)

    blocked = await moderate(update, context, text)
    if blocked:
        return

    await smart_reply(update, context, user_name, text)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle)
    )
    print("Evie is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
