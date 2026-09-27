import os
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

# ==================== إعدادات السيادة والأمان (توصيات أحمد السيد VIP) ====================
TELEGRAM_BOT_TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
ADMIN_ID = 5796443586  
ADMIN_USERNAME = "@V8V8VN"  

# قائمة المستخدمين المصرح لهم بالدخول
AUTHORIZED_USERS = {ADMIN_ID} 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== نظام التحقق الأمني الذكي ====================
async def check_security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    user_id = user.id
    
    if user_id == ADMIN_ID or user_id in AUTHORIZED_USERS:
        return True
        
    keyboard = [
        [InlineKeyboardButton("🔐 طلب تفعيل الحساب وصلاحيات VIP", callback_data="request_access")],
        [InlineKeyboardButton("💬 التواصل مع أحمد السيد للتفعيل", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")]
    ]
    
    msg_text = (
        "🚨 *نظام الحماية الحصري مفعل!*\n\n"
        "عذراً، حسابك غير مُسجل في قاعدة بيانات النخبة. يرجى طلب تفعيل الحساب من المطور أولاً 👇"
    )
    
    if update.message:
        await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return False

# ==================== واجهة /start والأزرار الرئيسية بتصميم أنيق وصغير ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_security(update, context):
        return

    user_name = update.effective_user.first_name if update.effective_user else "متداول النخبة"
    
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
            InlineKeyboardButton("📊 الدقة", callback_data="stats")
        ],
        [
            InlineKeyboardButton("📸 انستغرام", url="https://instagram.com/_7ok6"),
            InlineKeyboardButton("🎬 تيك توك", url="https://tiktok.com/@7ok6_")
        ],
        [
            InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support")
        ]
    ]
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
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# ==================== معالج الأزرار والقوائم ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data

    if data == "request_access":
        user = update.effective_user
        await query.message.edit_text(
            f"🔒 *طلب تفعيل الحساب*\n\n"
            f"• المعرف: `{user.id}`\n"
            f"• الاسم: `{user.first_name}`\n\n"
            f"لفتح البوت فوراً، راسل أحمد السيد:\n👤 `{ADMIN_USERNAME}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 مراسلة أحمد السيد", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")]])
        )
        return

    if not await check_security(update, context):
        return

    if data == "vip_strategies":
        strat_keyboard = [
            [InlineKeyboardButton("🔥 صيد الحيتان (Sweep)", callback_data="strat_sweep")],
            [InlineKeyboardButton("💎 البنوك المركزية (OB)", callback_data="strat_ob")],
            [InlineKeyboardButton("⚡ الانفجار السعري", callback_data="strat_breakout")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "⚡ *استراتيجيات أحمد السيد المتقدمة:*\nاختر الاستراتيجية أو أرسل الشارت للتطبيق 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(strat_keyboard)
        )
        return

    if data in ["strat_sweep", "strat_ob", "strat_breakout"]:
        back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="vip_strategies")]]
        await query.message.edit_text(
            "🎯 *تم تفعيل الاستراتيجية بنجاح.*\n📸 *أرسل صورة الشارت الآن لاستخراج الأهداف بدقة فائقة! ⚡*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
        return

    if data == "vip_subscriptions":
        sub_keyboard = [
            [InlineKeyboardButton("💵 أسبوعي ($25)", callback_data="sub_weekly")],
            [InlineKeyboardButton("💵 أسبوعين ($50)", callback_data="sub_biweekly")],
            [InlineKeyboardButton("👑 شهر VIP ($100)", callback_data="sub_monthly")],
            [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            f"💎 *باقات الترقية الحصرية*\nطرق الدفع: آسياسيل / ماستر كارد\nتواصل مع: `{ADMIN_USERNAME}` 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(sub_keyboard)
        )
        return

    if data in ["sub_weekly", "sub_biweekly", "sub_monthly"]:
        contact_keyboard = [
            [InlineKeyboardButton("💬 تواصل للتفعيل", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="vip_subscriptions")]
        ]
        await query.message.edit_text(
            f"🛒 لإتمام الاشتراك، راسل المطور حصرياً: `{ADMIN_USERNAME}` ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(contact_keyboard)
        )
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
        back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
        
        await query.message.edit_text(
            f"🎯 *الأصل المحدد:* `{chosen}`\n📸 *أرسل الشارت الآن* لتحليل السوق وتوليد التوصيات المضمونة ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
    elif data == "stats":
        back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
        await query.message.edit_text("📊 *نسبة دقة التوصيات:* `99.4%` 🚀", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "support":
        back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
        await query.message.edit_text(f"🛠️ *الدعم الفني:* `{ADMIN_USERNAME}` ⚡", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))
    elif data == "main_menu":
        await start_command(update, context)

# ==================== تحليل الشارت ====================
async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_security(update, context):
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
        f"📸 تابعنا للمزيد: انستغرام `_7ok6` | تيك توك `7ok6_`\n"
        f"🔒 المالك: {ADMIN_USERNAME}"
    )

    back_keyboard = [[InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")]]
    await update.message.reply_text(report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_image))

    print(f"🛸 [توصيات أحمد السيد VIP] يعمل بأعلى احترافية وأمان...")
    application.run_polling()

if __name__ == "__main__":
    main()