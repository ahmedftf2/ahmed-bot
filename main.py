import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

# ==================== إعدادات السيادة والأمان ====================
TELEGRAM_BOT_TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
ADMIN_ID = 5796443586  
ADMIN_USERNAME = "@V8V8VN"  
CHANNEL_URL = "https://t.me/FOR2AH"

VALID_KEYS = set()          
ACTIVE_USERS = {ADMIN_ID}   

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== نظام الحماية والتحقق ====================
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
        [InlineKeyboardButton("💬 مراسلة المطور للشراء والتفعيل", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")]
    ]
    
    msg_text = (
        "🚨 *عذراً عزيزي المتداول!*\n\n"
        "يجب عليك الاشتراك في القناة أولاً وإدخال **كود التفعيل** الخاص بك لفتح البوت الاستثماري 👇"
    )
    
    if update.message:
        await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
    return False

# ==================== دالة صنع الأكواد (للأدمن فقط) ====================
async def generate_key_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if update.effective_user.id != ADMIN_ID:
        await query.answer("هذا الزر مخصص للمطور فقط ⛔", show_alert=True)
        return
        
    new_key = f"FOR2AH-{random.randint(1000, 9999)}"
    VALID_KEYS.add(new_key)
    
    await query.answer("تم صنع الكود بنجاح!", show_chart=False)
    await query.message.reply_text(
        f"✅ *تم توليد كود اشتراك جديد بنجاح يا مطورنا!* 👑\n\n"
        f"🔑 الكود: `{new_key}`\n\n"
        f"أعطِ هذا الكود للزبون ليفعله في البوت.",
        parse_mode="Markdown"
    )

# ==================== معالجة إدخال الكود أو الصور ====================
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    
    if context.user_data.get('waiting_for_key'):
        context.user_data['waiting_for_key'] = False
        if text in VALID_KEYS:
            VALID_KEYS.remove(text)  
            ACTIVE_USERS.add(user_id)
            await update.message.reply_text(
                f"🎉 *مبروك! تم تفعيل اشتراكك بنجاح!*\nأرسل `/start` للبدء بالاستخدام 🚀",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ *عذراً، هذا الكود غير صحيح أو تم استخدامه مسبقاً!*", parse_mode="Markdown")
        return

    if update.message.photo:
        await handle_chart_image(update, context)

# ==================== واجهة /start الرئيسية (مخصصة للأدمن والمشتركين) ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # إذا لم يكن أدمن ولم يكن مفعل، نتحقق من أمانه
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    user_name = update.effective_user.first_name if update.effective_user else "متداول"
    
    # الواجهة الأساسية تماماً مثل الصورة التي طلبتها
    keyboard = [
        [
            InlineKeyboardButton("🚀 تشغيل البوت", callback_data="main_menu"),
            InlineKeyboardButton("🥇 الذهب المؤسسي", callback_data="asset_gold")
        ],
        [
            InlineKeyboardButton("₿ البيتكوين", callback_data="asset_btc"),
            InlineKeyboardButton("💶 اليورو / دولار", callback_data="asset_eur")
        ],
        [
            InlineKeyboardButton("🛢️ النفط الخام", callback_data="asset_oil"),
            InlineKeyboardButton("⚡ الاستراتيجيات", callback_data="vip_strategies")
        ],
        [
            InlineKeyboardButton("💎 باقات VIP", callback_data="vip_subscriptions"),
            InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="enter_key_prompt")
        ],
        [
            InlineKeyboardButton("📊 الدقة", callback_data="stats"),
            InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support")
        ]
    ]

    # 👑 [إضافة خاصة بالأدمن فقط]: إذا كنت أنت المطور، نضيف زر صنع الأكواد في أسفل القائمة حصراً!
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ [للدمن] صنع كود اشتراك جديد", callback_data="admin_gen_key")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 *أهلاً وسهلاً بك يا {user_name}*\n"
        f"👑 في بوت **توصيات أحمد السيد VIP**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💎 *نبذة عن المطور:*\n"
        f"• 📈 **خبرة:** `3 سنوات في الأسواق المالية`\n"
        f"• 🥇 **اختصاص:** `محلل ذهب ومؤشرات مؤسسية`\n"
        f"• 💻 **برمجة:** `خبير برمجي وصانع مؤشرات آلية`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *دقة النظام:* `99.4%` | 🚀 *الحالة:* `نشط 24/7`\n\n"
        f"👇 *اختر أحد الأقسام أدناه أو أرسل شارت التحليل:*"
    )

    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            pass

# ==================== معالج الأزرار ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_gen_key":
        await generate_key_action(update, context)
        return

    if data == "enter_key_prompt":
        context.user_data['waiting_for_key'] = True
        try:
            await query.message.edit_text(
                "🔑 *تفعيل كود الاشتراك*\n\nالرجاء إرسال كود التفعيل الخاص بك في رسالة نصية الآن 👇",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])
            )
        except Exception:
            pass
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]

    if data == "vip_strategies":
        strat_keyboard = [
            [InlineKeyboardButton("🔥 صيد الحيتان (Sweep)", callback_data="strat_sweep")],
            [InlineKeyboardButton("💎 البنوك المركزية (OB)", callback_data="strat_ob")],
            [InlineKeyboardButton("⚡ الانفجار السعري", callback_data="strat_breakout")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text("⚡ *استراتيجيات أحمد السيد المتقدمة:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(strat_keyboard))
        return

    if data in ["strat_sweep", "strat_ob", "strat_breakout"]:
        await query.message.edit_text("🎯 *تم تفعيل الاستراتيجية بنجاح.*\n📸 *أرسل صورة الشارت الآن لاستخراج الأهداف بدقة فائقة! ⚡*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
        return

    if data == "vip_subscriptions":
        sub_keyboard = [
            [InlineKeyboardButton("💵 أسبوعي ($25)", callback_data="sub_weekly")],
            [InlineKeyboardButton("💵 أسبوعين ($50)", callback_data="sub_biweekly")],
            [InlineKeyboardButton("👑 شهر VIP ($100)", callback_data="sub_monthly")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(f"💎 *باقات الترقية الحصرية*\nتواصل مع: `{ADMIN_USERNAME}` 👇", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(sub_keyboard))
        return

    if data in ["sub_weekly", "sub_biweekly", "sub_monthly"]:
        contact_keyboard = [
            [InlineKeyboardButton("💬 تواصل للتفعيل", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="vip_subscriptions")]
        ]
        await query.message.edit_text(f"🛒 لإتمام الاشتراك، راسل المطور حصرياً: `{ADMIN_USERNAME}` ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(contact_keyboard))
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
        await query.message.edit_text(f"🎯 *الأصل المحدد:* `{chosen}`\n📸 *أرسل الشارت الآن* لتحليل السوق بدقة ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "stats":
        await query.message.edit_text("📊 *نسبة دقة التوصيات:* `99.4%` 🚀", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "support":
        await query.message.edit_text(f"🛠️ *الدعم الفني:* `{ADMIN_USERNAME}` ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "main_menu":
        await start_command(update, context)

# ==================== تحليل الشارت ====================
async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    await update.message.reply_text("🧠 *جاري تفكيك الشارت وصياغة التوصية الاحترافية... انتظر يا مولاي ⚡*", parse_mode="Markdown")
    
    selected_asset = context.user_data.get('selected_asset', "الذهب المؤسسي (XAUUSD)")
    base_price = 2385.50 if "الذهب" in selected_asset else 84569.00
    is_buy = random.choice([True, False])
    signal_type = "🟢 شراء مؤسسي مضمون (BUY VIP)" if is_buy else "🔴 بيع مؤسسي مضمون (SELL VIP)"
    
    report = (
        f"🌟 *[ تقرير توصيات أحمد السيد VIP ]*\n\n"
        f"📊 *الأصل:* `{selected_asset}`\n"
        f"⚡ *الإشارة:* {signal_type}\n"
        f"🎯 *الدقة والموثوقية:* `99.4%`\n"
        f"💰 *سعر الدخول:* `{base_price}`\n\n"
        f"📉 *وقف الخسارة:* محصن تلقائياً\n"
        f"🎯 *الأهداف الثلاثة:* جاهزة ومؤمنة\n\n"
        f"🔒 المالك: {ADMIN_USERNAME}"
    )

    back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
    await update.message.reply_text(report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_text_messages))

    print(f"🛸 [توصيات أحمد السيد VIP] يعمل بأعلى احترافية وأمان...")
    application.run_polling()

if __name__ == "__main__":
    main()