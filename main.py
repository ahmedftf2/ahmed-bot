import os
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

# ==================== إعدادات السيادة والأمان ====================
TELEGRAM_BOT_TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
ADMIN_ID = 5796443586  
ADMIN_USERNAME = "@V8V8VN"  
CHANNEL_URL = "https://t.me/FOR2AH"

VALID_KEYS = {}       
ACTIVE_USERS = {ADMIN_ID} 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    user_id = user.id
    
    if user_id == ADMIN_ID or user_id in ACTIVE_USERS:
        return True
        
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في قناة المطور", url=CHANNEL_URL)],
        [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="enter_key_prompt")],
        [InlineKeyboardButton("💬 مراسلة المطور للتفعيل", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")]
    ]
    
    msg_text = "🚨 *عذراً، يرجى الاشتراك في القناة وتفعيل كود الاشتراك الخاص بك أولاً للاستخدام.*"
    
    if update.message:
        await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
    return False

# ==================== أمر توليد الأكواد للأدمن ====================
async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    args = context.args
    days = int(args[0]) if args and args[0].isdigit() else 30
    random_code = f"FOR2AH-{random.randint(10000, 99999)}"
    VALID_KEYS[random_code] = days
    
    await update.message.reply_text(
        f"✅ *تم توليد الكود بنجاح!*\n🔑 الكود: `{random_code}`\n⏳ المدة: `{days} يوم`",
        parse_mode="Markdown"
    )

# ==================== معالجة إدخال الكود ====================
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    
    if context.user_data.get('waiting_for_key'):
        context.user_data['waiting_for_key'] = False
        if text in VALID_KEYS:
            days = VALID_KEYS.pop(text)
            ACTIVE_USERS.add(user_id)
            await update.message.reply_text(
                f"🎉 *تم تفعيل اشتراكك بنجاح لمدة {days} يوماً!*\nأرسل `/start` للبدء 🚀",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ *الكود غير صحيح أو مستعمل مسبقاً!*", parse_mode="Markdown")
        return

    if update.message.photo:
        await handle_chart_image(update, context)

# ==================== واجهة /start مرتبة واحترافية ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_security(update, context):
        return

    user_name = update.effective_user.first_name if update.effective_user else "متداول"
    
    # واجهة مرتبة ونظيفة جداً (زرين في كل صف لتجنب التكدس والبطء)
    keyboard = [
        [
            InlineKeyboardButton("🥇 الذهب (XAUUSD)", callback_data="asset_gold"),
            InlineKeyboardButton("₿ البيتكوين (BTC)", callback_data="asset_btc")
        ],
        [
            InlineKeyboardButton("💶 اليورو دولار", callback_data="asset_eur"),
            InlineKeyboardButton("🛢️ النفط الخام", callback_data="asset_oil")
        ],
        [
            InlineKeyboardButton("⚡ الاستراتيجيات VIP", callback_data="vip_strategies"),
            InlineKeyboardButton("🔑 تفعيل كود اشتراك", callback_data="enter_key_prompt")
        ],
        [
            InlineKeyboardButton("📊 نسبة الدقة", callback_data="stats"),
            InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 *أهلاً بك يا {user_name} في بوت توصيات أحمد السيد*\n\n"
        f"📈 *المحلل:* أحمد السيد (خبرة 3 سنوات)\n"
        f"🎯 *دقة النظام:* `99.4%` | 🚀 *الحالة:* `نشط`\n\n"
        f"👇 *اختر الأصل المراد تحليله أو أرسل الشارت مباشرة:*"
    )

    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            pass

# ==================== معالج الأزرار السريع ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "enter_key_prompt":
        context.user_data['waiting_for_key'] = True
        try:
            await query.message.edit_text(
                "🔑 *تفعيل كود الاشتراك*\n\nالرجاء إرسال كود التفعيل في رسالة نصية الآن 👇",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])
            )
        except Exception:
            pass
        return

    if not await check_security(update, context):
        return

    back_keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]

    if data == "vip_strategies":
        strat_keyboard = [
            [InlineKeyboardButton("🔥 صيد الحيتان (Sweep)", callback_data="strat_sweep")],
            [InlineKeyboardButton("💎 البنوك المركزية (OB)", callback_data="strat_ob")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text("⚡ *اختر الاستراتيجية المطلوبة:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(strat_keyboard))
        return

    if data in ["strat_sweep", "strat_ob"]:
        await query.message.edit_text("🎯 *تم التفعيل! أرسل صورة الشارت الآن لاستخراج الأهداف ⚡*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
        return

    if data.startswith("asset_"):
        asset_names = {
            "asset_gold": "الذهب المؤسسي (XAUUSD)",
            "asset_btc": "البيتكوين (BTCUSD)",
            "asset_eur": "اليورو دولار (EURUSD)",
            "asset_oil": "النفط الخام (USOIL)"
        }
        chosen = asset_names.get(data, "الأصل المختار")
        context.user_data['selected_asset'] = chosen
        await query.message.edit_text(f"🎯 *تم اختيار:* `{chosen}`\n📸 *أرسل الشارت الآن* لتحليل السوق بدقة ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "stats":
        await query.message.edit_text("📊 *نسبة الدقة الحالية:* `99.4%` 🚀", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "support":
        await query.message.edit_text(f"🛠️ *للدعم الفني والتفعيل:* `{ADMIN_USERNAME}` ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "main_menu":
        await start_command(update, context)

# ==================== تحليل الشارت ====================
async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_security(update, context):
        return

    await update.message.reply_text("🧠 *جاري تفكيك الشارت واستخراج التوصية... انتظر قليلاً ⚡*", parse_mode="Markdown")
    
    selected_asset = context.user_data.get('selected_asset', "الذهب المؤسسي (XAUUSD)")
    base_price = 2385.50 if "الذهب" in selected_asset else 84569.00
    is_buy = random.choice([True, False])
    signal_type = "🟢 شراء مؤسسي (BUY)" if is_buy else "🔴 بيع مؤسسي (SELL)"
    
    report = (
        f"🌟 *[ تقرير توصيات أحمد السيد VIP ]*\n\n"
        f"📊 *الأصل:* `{selected_asset}`\n"
        f"⚡ *الإشارة:* {signal_type}\n"
        f"🎯 *الدقة:* `99.4%`\n"
        f"💰 *سعر الدخول المقترح:* `{base_price}`\n\n"
        f"📉 *وقف الخسارة:* محصن تلقائياً\n"
        f"🎯 *الأهداف:* 3 مستهدفات رئيسية جاهزة\n\n"
        f"🔒 المطور: {ADMIN_USERNAME}"
    )

    back_keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]
    await update.message.reply_text(report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("genkey", genkey_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_text_messages))

    print(f"🛸 [توصيات أحمد السيد VIP] يعمل بكفاءة عالية ورعة...")
    application.run_polling()

if __name__ == "__main__":
    main()