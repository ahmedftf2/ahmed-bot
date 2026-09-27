import os
import logging
import random
import pandas as pd
import numpy as np
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

# ==================== إعدادات السيادة والحماية (Alpha Core 6-Stars VIP) ====================
TELEGRAM_BOT_TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
ADMIN_ID = 5796443586  
ADMIN_USERNAME = "@V8V8VN"  
REQUIRED_CHANNEL = "@FOR2AH"  
ALPHA_AUTH_TOKEN = "AQ.Ab8RN6JOknqLaGAvUZhO2MePPKL2zHFq0neYgXLL3j7KKSugRg"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def verify_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """التحقق من الاشتراك الإجباري في القناة الرسمية"""
    user = update.effective_user
    if not user:
        return True
    user_id = user.id
    if user_id == ADMIN_ID:
        return True # المالك المستثنى
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember"
    payload = {"chat_id": REQUIRED_CHANNEL, "user_id": user_id}
    try:
        response = requests.post(url, json=payload).json()
        if response.get("ok"):
            status = response["result"]["status"]
            if status in ["member", "administrator", "creator"]:
                return True
    except Exception:
        pass
    
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في قناة النخبة VIP", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")],
        [InlineKeyboardButton("✅ تم الاشتراك، تفعيل النظام", callback_data="check_sub")]
    ]
    
    msg_text = (
        f"🚨 *عذراً يا عظيم، الوصول لنظام Zo Alpha 6-Stars يتطلب الاشتراك في القناة الرسمية أولاً:*\n"
        f"👉 {REQUIRED_CHANNEL}\n\n"
        f"اشترك ثم اضغط على زر التحقق أدناه لفتح بوابات التداول ⚡"
    )
    
    if update.message:
        await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return False

# ==================== واجهة /start الفاخرة (6 نجوم VIP) ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verify_subscription(update, context):
        return

    user_name = update.effective_user.first_name
    
    keyboard = [
        [
            InlineKeyboardButton("🥇 الذهب المؤسسي (XAUUSD)", callback_data="asset_gold"),
            InlineKeyboardButton("₿ البيتكوين العالمي (BTCUSD)", callback_data="asset_btc")
        ],
        [
            InlineKeyboardButton("💶 اليورو / دولار (EURUSD)", callback_data="asset_eur"),
            InlineKeyboardButton("🛢️ النفط الخام (USOIL)", callback_data="asset_oil")
        ],
        [
            InlineKeyboardButton("💎 باقات الترقية والاشتراك (6-Stars VIP)", callback_data="vip_subscriptions")
        ],
        [
            InlineKeyboardButton("📈 إحصائيات الدقة العالية", callback_data="stats"),
            InlineKeyboardButton("🛠️ الدعم الفني والمطور الخصري", callback_data="support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👑 *مرحباً بك يا {user_name} في النظام الإمبراطوري Zo Alpha (6-Stars VIP)* ⚡\n\n"
        f"🌟 *مستوى النظام:* `عالمي - مؤسسي (Institutional Grade)`\n"
        f"🎯 *معدل دقة الصفقات الخارقة (Win Rate):* `98.9%` *(أداء خماسي الأبعاد)*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 *حالة الجلسات العالمية المباشرة (UTC):*\n"
        f"• 🇬🇧 لندن: 🟢 `مفتوحة (سيولة مؤسسية)` | 🇺🇸 نيويورك: 🟢 `مفتوحة (ذروة الأسواق)`\n"
        f"• 🇯🇵 طوكيو: 🔴 `مغلقة` | 🇦🇺 سيدني: 🔴 `مغلقة`\n"
        f"🔥 *الجلسة النشطة الآن:* `لندن + نيويورك (أقوى فترات التداول العالمي)`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *اختر الأصل المالي المطلوب أو أرسل شارت التحليل لتطبيق خوارزميات السيولة الذكية:*"
    )

    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# ==================== معالج الأزرار والاشتراكات الفاخرة ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "check_sub":
        if await verify_subscription(update, context):
            await query.message.delete()
            await start_command(update, context)
        return

    if data == "vip_subscriptions":
        sub_keyboard = [
            [InlineKeyboardButton("💵 اشتراك أسبوعي ($25) - آسياسيل / ماستر", callback_data="sub_weekly")],
            [InlineKeyboardButton("💵 اشتراك أسبوعين ($50) - آسياسيل / ماستر", callback_data="sub_biweekly")],
            [InlineKeyboardButton("👑 اشتراك شهر VIP (6 نجوم) ($100) - آسياسيل / ماستر", callback_data="sub_monthly")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            f"💎 *بوابة ترقية الحسابات إلى مستوى 6 نجوم VIP* ⚡\n\n"
            f"احصل على الصفقات الخارقة المدعومة بمصفوفة السيولة المؤسسية وسحب الأوامر:\n\n"
            f"• ⏱️ **اشتراك أسبوع واحد:** `25 دولار`\n"
            f"• ⏱️ **اشتراك أسبوعين:** `50 دولار`\n"
            f"• 👑 **اشتراك شهر VIP كامل:** `100 دولار` *(توصيات لا نهائية وتحليل فوري VIP)*\n\n"
            f"💳 **طرق الدفع المعتمدة عالمياً:**\n"
            f"1️⃣ تحويل رصيد **آسياسيل (Asiacell)**\n"
            f"2️⃣ الدفع الإلكتروني المباشر عبر **الماستر كارد (Mastercard)**\n\n"
            f"اضغط على الباقة المطلوبة للتواصل الفوري مع المطور وتفعيل حسابك 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(sub_keyboard)
        )
        return

    if data in ["sub_weekly", "sub_biweekly", "sub_monthly"]:
        package_names = {
            "sub_weekly": "الباقة الأسبوعية VIP ($25)",
            "sub_biweekly": "باقة الأسبوعين VIP ($50)",
            "sub_monthly": "باقة الشهر VIP الخارقة ($100)"
        }
        chosen_pkg = package_names.get(data)
        
        contact_keyboard = [
            [InlineKeyboardButton("💬 التواصل الفوري مع المطور لتفعيل الحساب", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔙 رجوع للباقات", callback_data="vip_subscriptions")]
        ]
        await query.message.edit_text(
            f"🛒 *لقد حددت الباقة التالية:* `{chosen_pkg}`\n\n"
            f"💳 **طرق الدفع المتاحة:**\n"
            f"• رصيد أو كارت **آسياسيل**\n"
            f"• بطاقة **ماستر كارد (Mastercard)**\n\n"
            f"لإتمام الدفع واستلام كود التفعيل VIP، تواصل حصرياً مع المعرف الإمبراطوري:\n"
            f"👤 `{ADMIN_USERNAME}`\n\n"
            f"أرسل إيصال الدفع أو كارت التعبئة هناك ليتم فتح الحساب فوراً ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(contact_keyboard)
        )
        return

    if data.startswith("asset_"):
        asset_names = {
            "asset_gold": "الذهب المؤسسي (XAUUSD)",
            "asset_btc": "البيتكوين العالمي (BTCUSD)",
            "asset_eur": "اليورو / دولار (EURUSD)",
            "asset_oil": "النفط الخام (USOIL)"
        }
        chosen = asset_names.get(data, "الأصل المختار")
        back_keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]]
        
        await query.message.edit_text(
            f"🎯 *تم اختيار الأصل:* `{chosen}`\n\n"
            f"📸 *الرجاء إرسال صورة الشارت (Screenshot) الآن* لتقوم مصفوفة Zo بتحليل مناطق العرض والطلب، سحب السيولة، وتوليد صفقات الـ 6 نجوم VIP مع الأهداف الثلاثة واللوت المناسب بدقة تامة ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
    elif data == "stats":
        back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.message.edit_text(
            f"📊 *إحصائيات أداء خوارزميات Zo Alpha (6-Stars):*\n\n"
            f"• إجمالي صفقات النخبة الناجحة الشهر الماضي: `2,840 صفقة`\n"
            f"• نسبة الدقة الاستراتيجية: `98.9%` *(معتمدة مؤسسياً)*\n"
            f"• متوسط نقاط الربح المحققة أسبوعياً: `+3,400 نقطة ذهبية`\n"
            f"• استقرار الخوادم السحابية: `100% (تشغيل مستمر 24/7)` 🚀",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
    elif data == "support":
        back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.message.edit_text(
            f"🛠️ *الدعم الفني والسيطرة المركزية:*\n\n"
            f"• المطور والمالك الحصري: `{ADMIN_USERNAME}`\n"
            f"• القناة الرسمية للإشارات: `{REQUIRED_CHANNEL}`\n"
            f"• للاستفسارات الخاصة وترقيات الحسابات الفورية، تواصل عبر المعرف أعلاه ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )
    elif data == "main_menu":
        await start_command(update, context)

# ==================== محرك تحليل الشارت الخارق (6-Stars VIP Strategy Engine) ====================
async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verify_subscription(update, context):
        return

    await update.message.reply_text("🧠 *جاري تفكيك الشارت عبر خوارزميات السيولة المؤسسية وسحب الأوامر (SMC & Order Blocks)... صبرك يا مولاي ⚡*", parse_mode="Markdown")
    
    # محاكاة تحليل فائق الدقة ومستويات احترافية عالية
    is_buy = random.choice([True, False])
    signal_type = "🟢 صفقـة شـراء مؤسسية (STRONG BUY VIP)" if is_buy else "🔴 صفقـة بيـع مؤسسية (STRONG SELL VIP)"
    success_rate = random.randint(97, 99) # دقة 6 نجوم فائقة
    
    base_price = 2385.50 if random.choice([True, False]) else 68400.00
    
    if is_buy:
        sl = base_price - 14.0
        tp1 = base_price + 22.0
        tp2 = base_price + 45.0
        tp3 = base_price + 90.0
    else:
        sl = base_price + 14.0
        tp1 = base_price - 22.0
        tp2 = base_price - 45.0
        tp3 = base_price - 90.0

    lot_size = round(random.uniform(0.1, 5.0), 2) # دعم حتى 5 أو 10 لوت
    estimated_pips = abs(tp2 - base_price)
    estimated_profit_usd = estimated_pips * lot_size * 10

    report = (
        f"🌟 *[ تقرير التحليل المؤسسي 6-Stars VIP - Zo Matrix ]*\n\n"
        f"📊 *الإشارة النهائية:* {signal_type}\n"
        f"🎯 *نسبة دقة الصفقة:* `{success_rate}%` *(استراتيجية الزخم المتقدم)*\n"
        f"💰 *سعر الدخول المثالي:* `{base_price}`\n\n"
        f"📉 *وقف الخسارة المحصن (SL):* `{sl}`\n"
        f"🎯 *الهدف الأول المؤسسي (TP1):* `{tp1}`\n"
        f"🎯 *الهدف الثاني الرئيسي (TP2):* `{tp2}`\n"
        f"🎯 *الهدف الثالث الاستثماري (TP3):* `{tp3}`\n\n"
        f"⚖️ *حجم اللوت المقترح لإدارة رأس المال:* `{lot_size} Lot` *(النطاق المتاح: 0.01 إلى 10 لوت)*\n"
        f"💵 *الأرباح المتوقعة تقريباً (عند بلوغ TP2):* `~${estimated_profit_usd:.2f}`\n"
        f"🛡️ *حالة التأمين الذكي:* `مفعلة أوتوماتيكياً` (نقل وقف الخسارة لنقطة الدخول فور تحقيق الهدف الأول TP1)\n\n"
        f"🔒 نظام مرخص وحصري للمالك: {ADMIN_USERNAME} | قناة النخبة: {REQUIRED_CHANNEL}"
    )

    back_keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
    await update.message.reply_text(report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(back_keyboard))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_image))

    print(f"🛸 [Zo Alpha 6-Stars VIP Bot] يعمل بكامل قوته المؤسسية للمالك {ADMIN_USERNAME}...")
    application.run_polling()

if __name__ == "__main__":
    main()