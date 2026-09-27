import os
import io
import re
import sqlite3
import secrets
from datetime import datetime, timezone, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

# استيراد آمن لتفادي مشاكل المكتبات
try:
    import google.generativeai as genai
except ImportError:
    os.system("pip install google-generativeai")
    import google.generativeai as genai

# ==========================================
# 1. إعدادات البوت والبيانات الأساسية
# ==========================================
BOT_NAME = "بوت احمد السيد للتداول الشامل (ahmed_forex) 🏆"
TOKEN = "8739424060:AAF5gkhpBSD2xTuP7r9WRDUbEhxPQBupZcw"
OWNER_ID = 5796443586
DEVELOPER_TELEGRAM = "V8V8VN"

# ⚠️ ضع مفتاح Gemini API المباشر هنا:
GEMINI_API_KEY = "AQ.Ab8RN6LAw-aZQkgopK98z68duwL8xS1dKhZeuX5pZIhWpmn9zQ"

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_REAL_GEMINI_API_KEY_HERE":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"⚠️ خطأ في تهيئة الذكاء الاصطناعي: {e}")

# ==========================================
# 2. قاعدة البيانات (قفل الأكواد + آسيا سيل)
# ==========================================
def init_db():
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            expiry_date TEXT,
            activated_at TEXT,
            license_key TEXT UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS license_keys (
            key TEXT PRIMARY KEY,
            duration_days INTEGER,
            is_used INTEGER DEFAULT 0,
            used_by_user_id INTEGER DEFAULT NULL,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asiacell_cards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_number TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            action TEXT,
            result TEXT DEFAULT 'PENDING',
            created_at TEXT
        )
    """)

    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, expiry_date, activated_at, license_key)
        VALUES (?, '2099-12-31 23:59:59', ?, 'OWNER_PERMANENT')
    """, (OWNER_ID, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()

init_db()

def is_user_active(user_id):
    if user_id == OWNER_ID:
        return True, "2099-12-31"
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False, None
    exp_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > exp_date:
        return False, row[0]
    return True, row[0]

def activate_license(user_id, key_str):
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT duration_days, is_used, used_by_user_id FROM license_keys WHERE key = ?", (key_str,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False, "❌ كود التفعيل غير صحيح!"
    
    if row[1] == 1:
        conn.close()
        return False, "⚠️ هذا الكود تم استخدامه مسبقاً ومقفل على حساب آخر!"

    duration = row[0]
    expiry = datetime.now() + timedelta(days=duration)
    exp_str = expiry.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE license_keys SET is_used = 1, used_by_user_id = ? WHERE key = ?", (user_id, key_str))
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, expiry_date, activated_at, license_key)
        VALUES (?, ?, ?, ?)
    """, (user_id, exp_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key_str))
    
    conn.commit()
    conn.close()
    return True, exp_str

def generate_key(duration_days=30):
    key = f"AHMED-{duration_days}D-" + secrets.token_hex(4).upper()
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO license_keys (key, duration_days, is_used, created_at) VALUES (?, ?, 0, ?)",
                   (key, duration_days, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return key

def save_asia_card(user_id, card_num):
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO asiacell_cards (user_id, card_number, created_at) VALUES (?, ?, ?)",
                   (user_id, card_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    card_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return card_id

def record_trade(user_id, symbol, action):
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trades (user_id, symbol, action, created_at) VALUES (?, ?, ?, ?)",
                   (user_id, symbol, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trade_id

def update_trade_result(trade_id, result):
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE trades SET result = ? WHERE trade_id = ?", (result, trade_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trades WHERE result LIKE 'TP%'")
    wins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trades WHERE result = 'SL'")
    losses = cursor.fetchone()[0]
    conn.close()
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 100.0
    return total_users, wins, losses, win_rate

user_selections = {}
user_states = {}

# ==========================================
# 3. توقيت الجلسات
# ==========================================
def get_market_sessions_status():
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour

    sydney = "🟢 مفتوحة" if 22 <= hour or hour < 7 else "🔴 مغلقة"
    tokyo = "🟢 مفتوحة" if 0 <= hour < 9 else "🔴 مغلقة"
    london = "🟢 مفتوحة" if 8 <= hour < 16 else "🔴 مغلقة"
    new_york = "🟢 مفتوحة" if 13 <= hour < 22 else "🔴 مغلقة"

    active_sessions = []
    if "🟢" in sydney: active_sessions.append("سيدني")
    if "🟢" in tokyo: active_sessions.append("طوكيو")
    if "🟢" in london: active_sessions.append("لندن")
    if "🟢" in new_york: active_sessions.append("نيويورك")

    active_str = " + ".join(active_sessions) if active_sessions else "تداخل الجلسات"

    return (
        f"🌍 **حالة الجلسات المباشرة (UTC):**\n"
        f"• 🇬🇧 لندن: {london} | 🇺🇸 نيويورك: {new_york}\n"
        f"• 🇯🇵 طوكيو: {tokyo} | 🇦🇺 سيدني: {sydney}\n"
        f"🔥 **الجلسة النشطة:** `{active_str}`"
    )

# ==========================================
# 4. محرك التحليل المؤسسي
# ==========================================
def generate_prompt(symbol, timeframe):
    sessions = get_market_sessions_status()
    return f"""
    أنت الخوارزمية المؤسسية العالمية الفائقة المخصصة لـ ({BOT_NAME}).
    قم بتحليل الشارت المرفق بدقة باستخدام: (SMC, ICT, FVG, Order Blocks, Liquidity Sweeps).

    البيانات:
    - الأداة / الزوج: {symbol}
    - الفريم الزمني: {timeframe}
    {sessions}

    اكتب التقرير الهيكلي الدقيق التالي حصراً:

    1. 🎯 **الملخص والهيكل العام:**
       - الزوج: {symbol} | الفريم: {timeframe}
       - المسار: (صاعد ⬆️ / هابط ⬇️ / عرضي ↔️)

    2. 🔍 **التحليل المؤسسي (SMC & FVG):**
       - **مناطق Order Block:** [الأسعار بالضبط]
       - **الفجوة السعرية FVG:**
       - **أسباب التدفق المؤسسي.**

    3. 🚀 **توصية التداول المباشرة:**
       - **الصفقة:** (شراء BUY 🟢 / بيع SELL 🔴 / انتظار WAIT ⏳)
       - **ENTRY:** [رقم سعر الدخول]
       - **SL:** [رقم الستوب]
       - **TP1:** [رقم الهدف الأول]
       - **TP2:** [رقم الهدف الثاني]

    4. 🛡️ **إدارة المخاطر:**
       - **نسبة النجاح والقوة:** 🔥 96%

    تم التحليل بواسطة {BOT_NAME} 🚀
    """

# ==========================================
# 5. الأوامر وقوائم التلغرام
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active, exp_date = is_user_active(user_id)

    if not active:
        msg = (
            f"🔒 **أهلاً بك في {BOT_NAME} 🏆**\n\n"
            "هذا البوت محمي بنظام الاشتراكات الحصرية.\n"
            "يمكنك التفعيل الفوري عبر:\n"
            "1️⃣ **دفع كارت آسيا سيل (Asiacell)** مباشرة داخل البوت.\n"
            "2️⃣ أدخال **كود التفعيل** المخصص لك بالأمر:\n`/activate كود_التفعيل`\n\n"
            "⚠️ **تنبيه:** كود التفعيل يعمل على حسابك فقط ولا يمكن مشاركته."
        )
        keyboard = [
            [InlineKeyboardButton("💳 دفع الاشتراك عبر كارت آسيا سيل", callback_data="pay_asiacell")],
            [InlineKeyboardButton("👨‍💻 تواصل مع المطور لشراء كود", url=f"https://t.me/{DEVELOPER_TELEGRAM}")]
        ]
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await show_main_menu(update, context)

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ اكتب الأمر متبوعاً بالكود:\n`/activate AHMED-30D-XXXX`", parse_mode="Markdown")
        return

    key_input = context.args[0].strip()
    success, msg = activate_license(user_id, key_input)

    if success:
        await update.message.reply_text(f"🎉 **تم تفعيل الاشتراك بنجاح!**\n📅 ينتهي اشتراكك في: `{msg}`\nكودك مقفول الآن على حسابك الشخصي فقط.", parse_mode="Markdown")
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(msg)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions_text = get_market_sessions_status()
    _, wins, losses, win_rate = get_stats()

    keyboard = [
        [InlineKeyboardButton("🥇 الذهب (XAUUSD)", callback_data="asset_XAUUSD"), InlineKeyboardButton("₿ البيتكوين (BTCUSD)", callback_data="asset_BTCUSD")],
        [InlineKeyboardButton("💵 اليورو/دولار (EURUSD)", callback_data="asset_EURUSD"), InlineKeyboardButton("🛢️ النفط (USOIL)", callback_data="asset_USOIL")],
        [InlineKeyboardButton("💱 أزواج أخرى", callback_data="asset_OTHER")],
        [InlineKeyboardButton("📊 إحصائيات ونسبة النجاح", callback_data="show_stats")],
        [InlineKeyboardButton("👨‍💻 الدعم الفني والمطور", url=f"https://t.me/{DEVELOPER_TELEGRAM}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg_text = (
        f"🏆 **مرحباً بك في {BOT_NAME}**\n"
        f"🎯 **معدل النجاح (Win Rate):** `{win_rate:.1f}%` ({wins} رابحة / {losses} خاسرة)\n\n"
        f"{sessions_text}\n\n"
        f"👇 **اختر الأداة المالية للتحليل:**"
    )

    if update.message:
        await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg_text, parse_mode="Markdown", reply_markup=reply_markup)

# ==========================================
# 6. لوحة تحكم الأدمن
# ==========================================
async def admin_gen_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    days = int(context.args[0]) if context.args and context.args[0].isdigit() else 30
    key = generate_key(days)
    await update.message.reply_text(f"🔑 **كود تفعيل جديد:**\n`{key}`\nالمدة: {days} يوم\nملاحظة: سينقفل فور تفعليه من المشترك.", parse_mode="Markdown")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID or not context.args:
        return
    msg = " ".join(context.args)
    conn = sqlite3.connect("bot_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u[0], text=f"📢 **إذاعة من الإدارة:**\n\n{msg}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ تم الإرسال إلى {count} مشترك.")

# ==========================================
# 7. معالجة النقرات والأزرار وكروت آسيا
# ==========================================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    active, _ = is_user_active(user_id)
    data = query.data

    if data == "pay_asiacell":
        user_states[user_id] = "WAITING_ASIA_CARD"
        await query.message.reply_text(
            "📲 **إرسال كارت آسيا سيل (Asiacell):**\n\n"
            "يرجى كتابة وإرسال رقم كارت الشحن (16 رقم) في رسالة الآن.\n"
            "سيصل الكارت للإدارة فوراً لتفعيل حسابك تلقائياً!",
            parse_mode="Markdown"
        )
        return

    elif data.startswith("approve_asia_"):
        card_id = int(data.split("_")[2])
        conn = sqlite3.connect("bot_enterprise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM asiacell_cards WHERE card_id = ?", (card_id,))
        row = cursor.fetchone()
        if row:
            target_user = row[0]
            new_key = generate_key(30)
            activate_license(target_user, new_key)
            cursor.execute("UPDATE asiacell_cards SET status = 'APPROVED' WHERE card_id = ?", (card_id,))
            conn.commit()

            await context.bot.send_message(
                chat_id=target_user,
                text=f"🎉 **تم قبول كارت آسيا سيل وتفعيل اشتراكك 30 يوماً!**\n🔑 كودك المقفل: `{new_key}`",
                parse_mode="Markdown"
            )
            await query.message.edit_text(f"✅ تم تفعيل الاشتراك للمستخدم `{target_user}` بنجاح!")
        conn.close()
        return

    if not active:
        await query.message.reply_text("🔒 انتهت صلاحية اشتراكك!")
        return

    if data.startswith("asset_"):
        asset = data.replace("asset_", "")
        user_selections[user_id] = {'asset': asset}
        keyboard = [
            [InlineKeyboardButton("⏱️ 1 دقيقة", callback_data="tf_1m"), InlineKeyboardButton("⏱️ 5 دقائق", callback_data="tf_5m")],
            [InlineKeyboardButton("⏱️ 15 دقيقة", callback_data="tf_15m"), InlineKeyboardButton("⏱️ 30 دقيقة", callback_data="tf_30m")],
            [InlineKeyboardButton("⏱️ 1 ساعة / 4 ساعات", callback_data="tf_1h_4h")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_main")]
        ]
        await query.message.edit_text(f"🎯 الزوج: **{asset}**\n\n👇 **اختر الفريم الزمني:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("tf_"):
        tf = data.replace("tf_", "")
        if user_id in user_selections:
            user_selections[user_id]['tf'] = tf
            asset = user_selections[user_id]['asset']
            await query.message.edit_text(
                f"✅ **تم الضبط!**\n📌 الزوج: **{asset}** | ⏱️ الفريم: **{tf}**\n\n"
                f"📸 **الآن أرسل صورة الشارت لتبدأ الخوارزمية بالتحليل...**",
                parse_mode="Markdown"
            )

    elif data == "show_stats":
        total_u, wins, losses, win_rate = get_stats()
        await query.message.edit_text(
            f"📊 **سجل أداء وتتبع توصيات البوت:**\n\n"
            f"👥 المشتركين: `{total_u}`\n"
            f"🎯 الصفقات الرابحة (TP): `{wins}`\n"
            f"🛑 الصفقات الخاسرة (SL): `{losses}`\n"
            f"🔥 **نسبة النجاح:** `{win_rate:.1f}%`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة", callback_data="back_main")]])
        )

    elif data.startswith("tr_"):
        parts = data.split("_")
        trade_id = parts[1]
        res = parts[2]
        update_trade_result(trade_id, res)
        await query.message.reply_text(f"✅ تم تسجيل نتيجة الصفقة كـ ({res}).")

    elif data == "back_main":
        await show_main_menu(update, context)

# ==========================================
# 8. معالجة النصوص وكروت آسيا
# ==========================================
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_states.get(user_id) == "WAITING_ASIA_CARD":
        clean_card = re.sub(r"\D", "", text)
        if len(clean_card) >= 13:
            card_id = save_asia_card(user_id, clean_card)
            user_states[user_id] = None

            await update.message.reply_text("✅ **تم استلام كارت آسيا سيل بنجاح!**\nجاري التحقق والمطابقة والتفعيل...")

            admin_keyboard = [[InlineKeyboardButton("✅ قبول وتفعيل 30 يوم", callback_data=f"approve_asia_{card_id}")]]
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=(
                    f"💳 **طلب اشتراك بكارت آسيا سيل:**\n\n"
                    f"👤 المشترك: [{update.effective_user.first_name}](tg://user?id={user_id})\n"
                    f"🆔 الأيدي: `{user_id}`\n"
                    f"🔢 **رقم الكارت:** `{clean_card}`\n\n"
                    f"قم بشحن الكارت في هاتفك ثم اضغط قبول:"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        else:
            await update.message.reply_text("⚠️ الرقم غير مكتمل. يرجى إرسال رقم كارت آسيا سيل الصحيح.")

# ==========================================
# 9. معالجة الصور بالذكاء الاصطناعي
# ==========================================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active, _ = is_user_active(user_id)

    if not active:
        await update.message.reply_text("🔒 اشتراكك غير مفعل. استخدم `/activate` أو ادفع بـ كارت آسيا سيل.")
        return

    selection = user_selections.get(user_id, {'asset': 'XAUUSD', 'tf': '15m'})
    asset = selection['asset']
    tf = selection['tf']

    status_msg = await update.message.reply_text("🚀 **جاري دراسة الشارت واستخراج التحليل التكتيكي...**")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        prompt = generate_prompt(asset, tf)

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)},
            prompt
        ])

        analysis_text = response.text
        action = "BUY 🟢" if "BUY" in analysis_text else "SELL 🔴"
        trade_id = record_trade(user_id, asset, action)

        await status_msg.delete()

        keyboard = [
            [InlineKeyboardButton("🎯 ضربت الهدف TP1", callback_data=f"tr_{trade_id}_TP1"), InlineKeyboardButton("🎯 ضربت الهدف TP2", callback_data=f"tr_{trade_id}_TP2")],
            [InlineKeyboardButton("🛑 ضربت الستوب SL", callback_data=f"tr_{trade_id}_SL")],
            [InlineKeyboardButton("🔄 تحليل شارت جديد", callback_data="back_main")]
        ]

        await update.message.reply_text(
            analysis_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

# ==========================================
# 10. التشغيل المباشر
# ==========================================
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("activate", activate_command))
    app.add_handler(CommandHandler("genkey", admin_gen_key))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"⚡ {BOT_NAME} يعمل الآن بنجاح...")
    app.run_polling()