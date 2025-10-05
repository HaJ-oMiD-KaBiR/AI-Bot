from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes,
    filters, ChatMemberHandler
)
import asyncio
import requests
import urllib.parse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "7556525917:AAHdkZ9O6J84jmauzM1jhNm5or6eKHxS6Qo"
CHANNEL_ID = "@Justice_died"
SUPPORT_USERNAME = "ruzered"

# بررسی عضویت در کانال
async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, update.effective_user.id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# پیام ورود ربات به گروه
async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.my_chat_member.chat
    new_status = update.my_chat_member.new_chat_member.status

    if chat.type in ["group", "supergroup"] and new_status == "administrator":
        title = chat.title

        try:
            if chat.username:
                group_link = f"https://t.me/{chat.username}"
            else:
                group_link = await context.bot.export_chat_invite_link(chat.id)

            group_mention = f'<a href="{group_link}">{title}</a>'
        except:
            group_mention = title

        text = (
            f"<b>ربات با موفقیت در گروه {group_mention} اضافه شد.</b>\n\n"
            f"<b>من هوش مصنوعی KaBiR AI هستم و آماده پاسخ به سوالات شما..!</b>\n\n"
            f"<blockquote>لطفاً قبل از سوال پرسیدن از کلمه ''جیمی'' استفاده کنید، مثال :\nجیمی ۵ کشور پرجمعیت جهان رو نام ببر</blockquote>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛠 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ])

        await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


# پاسخ به پیام‌های متنی در گروه یا پیوی
async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_type = message.chat.type
    text = message.text.strip()

    if chat_type in ["group", "supergroup"]:
        if not await is_member(update, context):
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("Justice died 🖤", url="https://t.me/Justice_died")]
            ])
            await message.reply_text(
                "برای استفاده از ربات حتماً در کانال عضو شوید 👇",
                reply_markup=join_button
            )
            return

        lowered = text.lower()
        if not (lowered.startswith("جیمی") or lowered.startswith("jimi")):
            return

        cleaned = text[len("جیمی "):] if text.lower().startswith("جیمی") else text[len("jimi "):]
    else:
        cleaned = text 
        
        await message.chat.send_action(action="typing")

    url = f"https://hoshi-app.ir/api/chat-gpt.php?text={urllib.parse.quote(cleaned)}"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", "❌ جوابی نیومد.")
        else:
            result = "لطفاً سوال خود را بپرسید."
    except Exception as e:
        result = f"❌ ارور اتصال: {e}"

    await message.reply_text(result, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛠 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ])
        await update.message.reply_text(
            "*سلام ✌️*\n"
            "*من یک ربات هوش مصنوعی رایگان هستم که توسط HaJ oMiD نوشته شده*\n\n"
            "*لطفاً سوال خودتون رو بپرسید :*",
            parse_mode="Markdown", 
            reply_markup=keyboard
        )
        

# اجرای ربات
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(ChatMemberHandler(bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt))
app.run_polling()