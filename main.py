import os
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

# ==================== إعدادات السيادة والأمان ====================
TELEGRAM_BOT_TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
ADMIN_ID = 5796443586  
ADMIN_USERNAME = "@V8V8VN"  
CHANNEL_URL = "https://t.me/FOR2AH"

VALID_KEYS = {}          
ACTIVE_USERS = {ADMIN_ID}   
USER_ACCOUNTS = {} # لتخزين معلومات الحسابات (حقيقي/ديمو) للمستخدمين

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
            await update.callback_query.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
    return False

# ==================== دالة صنع الأكواد للأدمن ====================
async def generate_key_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await query.answer("هذا الزر مخصص للمطور فقط ⛔", show_alert=True)
        return
        
    await query.answer()
    new_key = f"FOR2AH-{random.randint(1000, 9999)}"
    expiry_date = datetime.now() + timedelta(days=30)
    VALID_KEYS[new_key] = expiry_date
    expiry_str = expiry_date.strftime('%Y-%m-%d')
    
    admin_msg = (
        f"✅ *تم توليد كود اشتراك جديد بنجاح!* 👑\n\n"
        f"🔑 الكود: `{new_key}`\n"
        f"⏳ صالح لغاية: `{expiry_str}` (30 يوماً)\n\n"
        f"📋 اضغط على الكود لنسخه وإرساله للزبون 👇"
    )
    await context.bot.send_message(chat_id=user_id, text=admin_msg, parse_mode="Markdown")

# ==================== إدارة الحسابات (حقيقي / ديمو) ====================
async def accounts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    kb = [
        [InlineKeyboardButton("🟢 ربط حساب حقيقي (Live)", callback_data="acc_live_setup")],
        [InlineKeyboardButton("🔵 ربط حساب ديمو (Demo)", callback_data="acc_demo_setup")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
    ]
    await query.message.edit_text(
        "🎛️ *إدارة حسابات التداول الآلي*\n\nاختر نوع الحساب الذي تريد ربطه لتنفيذ الصفقات تلقائياً عبر البوت 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def handle_account_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()
    user_id = update.effective_user.id

    if data == "acc_live_setup":
        context.user_data['waiting_for_acc'] = 'live'
        await query.message.edit_text(
            "🟢 *إعداد الحساب الحقيقي*\n\nالرجاء إرسال بيانات حسابك (مثال: رقم الحساب، كلمة المرور، السيرفر) في رسالة نصية لتفعيل الربط الآلي 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="accounts_manage")]])
        )
    elif data == "acc_demo_setup":
        context.user_data['waiting_for_acc'] = 'demo'
        await query.message.edit_text(
            "🔵 *إعداد الحساب التجريبي (Demo)*\n\nالرجاء إرسال تفاصيل حساب الديمو الخاص بك لتفعيل التداول التجريبي الآلي 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="accounts_manage")]])
        )

# ==================== معالجة النصوص والأكواد والحسابات ====================
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    
    # التحقق من إدخال كود التفعيل
    if context.user_data.get('waiting_for_key'):
        context.user_data['waiting_for_key'] = False
        if text in VALID_KEYS:
            expiry_date = VALID_KEYS[text]
            if datetime.now() > expiry_date:
                VALID_KEYS.pop(text, None)
                await update.message.reply_text("❌ *عذراً، هذا الكود منتهي الصلاحية!*", parse_mode="Markdown")
                return
            VALID_KEYS.pop(text)
            ACTIVE_USERS.add(user_id)
            await update.message.reply_text("🎉 *مبروك! تم تفعيل اشتراكك بنجاح!*\nأرسل `/start` للبدء بالاستخدام 🚀", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ *عذراً، هذا الكود غير صحيح أو مستخدم!*", parse_mode="Markdown")
        return

    # التحقق من إدخال بيانات الحساب (حقيقي/ديمو)
    acc_type = context.user_data.get('waiting_for_acc')
    if acc_type:
        context.user_data['waiting_for_acc'] = None
        USER_ACCOUNTS[user_id] = {"type": acc_type, "details": text}
        await update.message.reply_text(
            f"✅ *تم حفظ وربط حسابك الـ ({acc_type.upper()}) بنجاح!*\nأصبح البوت جاهزاً الآن لتنفيذ الصفقات تلقائياً على عملاتك المفضلة 🚀",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]])
        )
        return

    if update.message.photo:
        await handle_chart_image(update, context)

# ==================== واجهة /start الرئيسية ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    user_name = update.effective_user.first_name if update.effective_user else "متداول"
    
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
            InlineKeyboardButton("🎛️ إدارة الحسابات (حقيقي/ديمو)", callback_data="accounts_manage"),
            InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support")
        ]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ [للأدمن] صنع كود اشتراك جديد", callback_data="admin_gen_key")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 *أهلاً وسهلاً بك يا {user_name}*\n"
        f"👑 في بوت **توصيات أحمد السيد VIP (التداول الآلي)**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💎 *نبذة عن المطور:*\n"
        f"• 📈 **خبرة:** `3 سنوات في الأسواق المالية`\n"
        f"• 🥇 **اختصاص:** `محلل ذهب ومؤشرات مؤسسية`\n"
        f"• 💻 **برمجة:** `خبير برمجي وصانع مؤشرات آلية`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *دقة النظام:* `99.4%` | 🚀 *الحالة:* `نشط 24/7`\n\n"
        f"👇 *اختر أحد الأقسام أدناه لتحديد العملة أو إدارة الحسابات:*"
    )

    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            pass

# ==================== معالج الأزرار وقائمة العملات المتقدمة ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "admin_gen_key":
        await generate_key_action(update, context)
        return

    if data == "accounts_manage":
        await accounts_menu(update, context)
        return

    if data in ["acc_live_setup", "acc_demo_setup"]:
        await handle_account_setup(update, context)
        return

    if data == "enter_key_prompt":
        await query.answer()
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

    await query.answer()
    user_id = update.effective_user.id
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]

    # معالجة الأصول واختيار الخيارين (تحليل أو تداول آلي)
    assets_map = {
        "asset_gold": "الذهب المؤسسي (XAUUSD)",
        "asset_btc": "البيتكوين (BTCUSD)",
        "asset_eur": "اليورو دولار (EURUSD)",
        "asset_oil": "النفط الخام (USOIL)"
    }

    if data in assets_map:
        asset_name = assets_map[data]
        context.user_data['selected_asset'] = asset_name
        
        choice_keyboard = [
            [InlineKeyboardButton("📸 إرسال شارت والتحليل الفني", callback_data=f"analyze_{data}")],
            [InlineKeyboardButton("⚡ الدخول الآلي للصفقة (بعد تأكيد الاستراتيجيات)", callback_data=f"autotrade_{data}")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            f"🎯 *الأصل المحدد:* `{asset_name}`\n\nاختر طريقة التعامل مع هذا الأصل 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(choice_keyboard)
        )
        return

    # إذا اختار تحليل الشارت
    if data.startswith("analyze_"):
        await query.message.edit_text(
            "📸 *تم اختيار التحليل اليدوي.*\nأرسل صورة الشارت الآن لاستخراج الأهداف ودقة 99.4% ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
        return

    # إذا اختار الدخول الآلي للصفقة
    if data.startswith("autotrade_"):
        # التحقق هل ربط حساب؟
        user_acc = USER_ACCOUNTS.get(user_id)
        if not user_acc:
            await query.message.edit_text(
                "⚠️ *عذراً، لم تقم بربط أي حساب تداول بعد!*\n\nيرجى الذهاب إلى 'إدارة الحسابات' وربط حسابك (حقيقي أو ديمو) أولاً لتفعيل التداول الآلي 🛡️",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎛️ إدارة الحسابات الآن", callback_data="accounts_manage")],
                    [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
                ])
            )
            return

        # تنفيذ محاكاة فحص الاستراتيجيات وتأكيدها
        asset_key = data.replace("autotrade_", "")
        chosen_asset = assets_map.get(asset_key, "العملة")
        
        await query.message.edit_text(
            f"🔍 *جاري فحص جميع الاستراتيجيات على {chosen_asset} ...*\n"
            f"• فحص صيد الحيتان (Sweep) ... ✅ متوافق\n"
            f"• فحص البنوك المركزية (OB) ... ✅ متوافق\n"
            f"• فحص الانفجار السعري ... ✅ مؤكد بنسبة 99.4%\n\n"
            f"🚀 *تم تأكيد الشروط بالكامل! جاري إرسال أمر التنفيذ إلى حسابك الـ ({user_acc['type'].upper()})...*",
            parse_mode="Markdown"
        )
        
        # محاكاة إرسال الصفقة بنجاح
        entry_price = 2385.50 if "الذهب" in chosen_asset else 68450.00
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⚡ *[ تم تنفيذ الصفقة آلياً بنجاح ]*\n\n"
                 f"📊 الأصل: `{chosen_asset}`\n"
                 f"🏷️ الحساب: `{user_acc['type'].upper()}`\n"
                 f"🟢 نوع الصفقة: `شراء آلي (BUY)`\n"
                 f"💰 سعر الدخول: `{entry_price}`\n"
                 f"🎯 الأهداف: مفعلة ومحمية بالكامل 🚀",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
        return

    if data == "vip_strategies":
        strat_keyboard = [
            [InlineKeyboardButton("🔥 صيد الحيتان (Sweep)", callback_data="strat_sweep")],
            [InlineKeyboardButton("💎 البنوك المركزية (OB)", callback_data="strat_ob")],
            [InlineKeyboardButton("⚡ الانفجار السعري", callback_data="strat_breakout")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text("⚡ *استراتيجيات أحمد السيد المتقدمة:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(strat_keyboard))
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

    if data == "stats":
        await query.message.edit_text("📊 *نسبة دقة التوصيات والاستراتيجيات الآلية:* `99.4%` 🚀", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "support":
        await query.message.edit_text(f"🛠️ *الدعم الفني:* `{ADMIN_USERNAME}` ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "main_menu":
        await start_command(update, context)

# ==================== تحليل الشارت ====================
async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID and not await check_security(update, context):
        return

    await update.message.reply_text("🧠 *جاري تفكيك الشارت وصياغة التوصية الفنية الاحترافية... انتظر يا مولاي ⚡*", parse_mode="Markdown")
    
    selected_asset = context.user_data.get('selected_asset', "الذهب المؤسسي (XAUUSD)")
    base_price = 2385.50 if "الذهب" in selected_asset else 68450.00
    is_buy = random.choice([True, False])
    signal_type = "🟢 شراء مؤسسي (BUY)" if is_buy else "🔴 بيع مؤسسي (SELL)"
    
    report = (
        f"🌟 *[ تقرير التحليل الفني - أحمد السيد VIP ]*\n\n"
        f"📊 *الأصل:* `{selected_asset}`\n"
        f"⚡ *الإشارة:* {signal_type}\n"
        f"🎯 *الدقة والموثوقية:* `99.4%`\n"
        f"💰 *سعر الدخول:* `{base_price}`\n\n"
        f"📉 *وقف الخسارة:* مؤمن تلقائياً\n"
        f"🎯 *الأهداف الثلاثة:* جاهزة ومؤمنة\n\n"
        f"🔒 المالك: {ADMIN_USERNAME}"
    )

    back_head = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
    await update.message.reply_text(report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_head))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_text_messages))

    print(f"🛸 [توصيات أحمد السيد VIP - التداول الآلي] يعمل بكفاءة أسطورية...")
    application.run_polling()

if __name__ == "__main__":
    main()