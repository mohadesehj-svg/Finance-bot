import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, ContextTypes, filters
)
from supabase import create_client, Client

# ─── تنظیمات ───────────────────────────────────────────────
BOT_TOKEN = "8042445672:AAHmBHG2fI08vrdIGnambUfX-S5Pob5egWA"
SUPABASE_URL = "https://xnadhiqnrsjgwxvdjwyj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhuYWRoaXFucnNqZ3d4dmRqd3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEwNzcyNzksImV4cCI6MjA5NjY1MzI3OX0.BYqP768Ns5htizmjOU_3L3sQ8S7hCJbciFoP0reuM9U"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(level=logging.INFO)

# ─── Health Check Server برای Render ──────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ─── مراحل مکالمه ──────────────────────────────────────────
(
    MAT_NAME, MAT_UNIT, MAT_PRICE,
    EDIT_MAT_CHOOSE, EDIT_MAT_FIELD, EDIT_MAT_VALUE,
    SEC_NAME, SEC_VALUE, SEC_TYPE,
    EDIT_SEC_CHOOSE, EDIT_SEC_FIELD, EDIT_SEC_VALUE,
    CALC_INPUT
) = range(13)

# ═══════════════════════════════════════════════════════════
#  /start  —  منوی اصلی
# ═══════════════════════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("➕ افزودن ماده خام", callback_data="add_mat"),
         InlineKeyboardButton("📋 لیست مواد خام", callback_data="list_mat")],
        [InlineKeyboardButton("✏️ ویرایش ماده خام", callback_data="edit_mat"),
         InlineKeyboardButton("🗑 حذف ماده خام", callback_data="del_mat")],
        [InlineKeyboardButton("➕ افزودن هزینه ثانویه", callback_data="add_sec"),
         InlineKeyboardButton("📋 لیست هزینه‌های ثانویه", callback_data="list_sec")],
        [InlineKeyboardButton("✏️ ویرایش هزینه ثانویه", callback_data="edit_sec"),
         InlineKeyboardButton("🗑 حذف هزینه ثانویه", callback_data="del_sec")],
        [InlineKeyboardButton("🧮 محاسبه قیمت محصول", callback_data="calc")],
    ]
    await update.effective_message.reply_text(
        "سلام! 👋\nبه ربات حسابگر مالی خوش اومدی.\nچیکار می‌خوای انجام بدی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ═══════════════════════════════════════════════════════════
#  افزودن ماده خام
# ═══════════════════════════════════════════════════════════
async def add_mat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("اسم ماده خام رو بنویس:\n(برای لغو /cancel بزن)")
    return MAT_NAME

async def mat_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["mat_name"] = update.message.text.strip()
    await update.message.reply_text("واحد اندازه‌گیری رو بنویس (مثلاً: گرم، سانتیمتر، عدد):")
    return MAT_UNIT

async def mat_unit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["mat_unit"] = update.message.text.strip()
    await update.message.reply_text("قیمت به ازای هر واحد رو بنویس (عدد، به تومان):")
    return MAT_PRICE

async def mat_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.strip().replace(",", ""))
    except ValueError:
        await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کن:")
        return MAT_PRICE
    supabase.table("materials").insert({
        "name": ctx.user_data["mat_name"],
        "unit": ctx.user_data["mat_unit"],
        "price_per_unit": price
    }).execute()
    await update.message.reply_text(
        f"✅ ماده خام «{ctx.user_data['mat_name']}» با موفقیت ثبت شد!\n\n"
        f"واحد: {ctx.user_data['mat_unit']}\nقیمت هر واحد: {price:,.0f} تومان"
    )
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  لیست مواد خام
# ═══════════════════════════════════════════════════════════
async def list_mat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("materials").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز ماده خامی ثبت نشده.")
        return
    txt = "📋 *لیست مواد خام:*\n\n"
    for r in rows:
        txt += f"• *{r['name']}* — هر {r['unit']}: {float(r['price_per_unit']):,.0f} تومان\n"
    await update.callback_query.message.reply_text(txt, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
#  ویرایش ماده خام
# ═══════════════════════════════════════════════════════════
async def edit_mat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("materials").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز ماده خامی ثبت نشده.")
        return ConversationHandler.END
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"emat_{r['id']}")] for r in rows]
    await update.callback_query.message.reply_text(
        "کدوم ماده خام رو می‌خوای ویرایش کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return EDIT_MAT_CHOOSE

async def edit_mat_choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    mat_id = int(update.callback_query.data.replace("emat_", ""))
    ctx.user_data["edit_mat_id"] = mat_id
    kb = [
        [InlineKeyboardButton("اسم", callback_data="efield_name"),
         InlineKeyboardButton("واحد", callback_data="efield_unit"),
         InlineKeyboardButton("قیمت", callback_data="efield_price")]
    ]
    await update.callback_query.message.reply_text(
        "کدوم فیلد رو ویرایش کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return EDIT_MAT_FIELD

async def edit_mat_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    ctx.user_data["edit_mat_field"] = update.callback_query.data.replace("efield_", "")
    labels = {"name": "اسم جدید", "unit": "واحد جدید", "price": "قیمت جدید (عدد)"}
    await update.callback_query.message.reply_text(
        f"{labels[ctx.user_data['edit_mat_field']]} رو بنویس:"
    )
    return EDIT_MAT_VALUE

async def edit_mat_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    field = ctx.user_data["edit_mat_field"]
    val = update.message.text.strip().replace(",", "")
    db_field = "price_per_unit" if field == "price" else field
    if field == "price":
        try:
            val = float(val)
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کن:")
            return EDIT_MAT_VALUE
    supabase.table("materials").update({db_field: val}).eq("id", ctx.user_data["edit_mat_id"]).execute()
    await update.message.reply_text("✅ ماده خام با موفقیت ویرایش شد!")
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  حذف ماده خام
# ═══════════════════════════════════════════════════════════
async def del_mat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("materials").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز ماده خامی ثبت نشده.")
        return
    kb = [[InlineKeyboardButton(f"🗑 {r['name']}", callback_data=f"dmat_{r['id']}")] for r in rows]
    await update.callback_query.message.reply_text(
        "کدوم ماده خام رو حذف کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def del_mat_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    mat_id = int(update.callback_query.data.replace("dmat_", ""))
    supabase.table("materials").delete().eq("id", mat_id).execute()
    await update.callback_query.message.reply_text("✅ ماده خام حذف شد.")

# ═══════════════════════════════════════════════════════════
#  افزودن هزینه ثانویه
# ═══════════════════════════════════════════════════════════
async def add_sec_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "اسم هزینه ثانویه رو بنویس:\n(مثلاً: سود، دستمزد، بسته‌بندی، ارسال)\n\n(برای لغو /cancel بزن)"
    )
    return SEC_NAME

async def sec_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["sec_name"] = update.message.text.strip()
    kb = [
        [InlineKeyboardButton("💰 مبلغ ثابت (تومان)", callback_data="stype_fixed"),
         InlineKeyboardButton("📊 درصد از هزینه اولیه", callback_data="stype_percent")]
    ]
    await update.message.reply_text("نوع هزینه رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(kb))
    return SEC_TYPE

async def sec_type(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    ctx.user_data["sec_type"] = update.callback_query.data.replace("stype_", "")
    label = "مبلغ (تومان)" if ctx.user_data["sec_type"] == "fixed" else "درصد (مثلاً ۲۰ برای ۲۰٪)"
    await update.callback_query.message.reply_text(f"{label} رو وارد کن:")
    return SEC_VALUE

async def sec_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text.strip().replace(",", ""))
    except ValueError:
        await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کن:")
        return SEC_VALUE
    supabase.table("secondary_costs").insert({
        "name": ctx.user_data["sec_name"],
        "value": val,
        "type": ctx.user_data["sec_type"]
    }).execute()
    type_label = "تومان ثابت" if ctx.user_data["sec_type"] == "fixed" else "درصد"
    await update.message.reply_text(
        f"✅ هزینه «{ctx.user_data['sec_name']}» ثبت شد!\nمقدار: {val:,.0f} {type_label}"
    )
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  لیست هزینه‌های ثانویه
# ═══════════════════════════════════════════════════════════
async def list_sec(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("secondary_costs").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
        return
    txt = "📋 *هزینه‌های ثانویه:*\n\n"
    for r in rows:
        t = "٪" if r["type"] == "percent" else " تومان"
        txt += f"• *{r['name']}*: {float(r['value']):,.0f}{t}\n"
    await update.callback_query.message.reply_text(txt, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
#  ویرایش هزینه ثانویه
# ═══════════════════════════════════════════════════════════
async def edit_sec_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("secondary_costs").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
        return ConversationHandler.END
    kb = [[InlineKeyboardButton(r["name"], callback_data=f"esec_{r['id']}")] for r in rows]
    await update.callback_query.message.reply_text(
        "کدوم هزینه رو ویرایش کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return EDIT_SEC_CHOOSE

async def edit_sec_choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    ctx.user_data["edit_sec_id"] = int(update.callback_query.data.replace("esec_", ""))
    kb = [
        [InlineKeyboardButton("اسم", callback_data="sedit_name"),
         InlineKeyboardButton("مقدار", callback_data="sedit_value"),
         InlineKeyboardButton("نوع", callback_data="sedit_type")]
    ]
    await update.callback_query.message.reply_text(
        "کدوم فیلد رو ویرایش کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return EDIT_SEC_FIELD

async def edit_sec_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    field = update.callback_query.data.replace("sedit_", "")
    ctx.user_data["edit_sec_field"] = field
    if field == "type":
        kb = [
            [InlineKeyboardButton("💰 مبلغ ثابت", callback_data="sntype_fixed"),
             InlineKeyboardButton("📊 درصد", callback_data="sntype_percent")]
        ]
        await update.callback_query.message.reply_text("نوع جدید رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(kb))
    else:
        labels = {"name": "اسم جدید", "value": "مقدار جدید (عدد)"}
        await update.callback_query.message.reply_text(f"{labels[field]} رو بنویس:")
    return EDIT_SEC_VALUE

async def edit_sec_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    field = ctx.user_data["edit_sec_field"]
    if update.callback_query:
        await update.callback_query.answer()
        val = update.callback_query.data.replace("sntype_", "")
    else:
        val = update.message.text.strip().replace(",", "")
        if field == "value":
            try:
                val = float(val)
            except ValueError:
                await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کن:")
                return EDIT_SEC_VALUE
    supabase.table("secondary_costs").update({field: val}).eq("id", ctx.user_data["edit_sec_id"]).execute()
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text("✅ هزینه ثانویه با موفقیت ویرایش شد!")
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  حذف هزینه ثانویه
# ═══════════════════════════════════════════════════════════
async def del_sec(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("secondary_costs").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
        return
    kb = [[InlineKeyboardButton(f"🗑 {r['name']}", callback_data=f"dsec_{r['id']}")] for r in rows]
    await update.callback_query.message.reply_text(
        "کدوم هزینه رو حذف کنی؟",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def del_sec_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    sec_id = int(update.callback_query.data.replace("dsec_", ""))
    supabase.table("secondary_costs").delete().eq("id", sec_id).execute()
    await update.callback_query.message.reply_text("✅ هزینه ثانویه حذف شد.")

# ═══════════════════════════════════════════════════════════
#  محاسبه قیمت محصول
# ═══════════════════════════════════════════════════════════
async def calc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    rows = supabase.table("materials").select("*").order("name").execute().data
    if not rows:
        await update.callback_query.message.reply_text("ابتدا مواد خام رو ثبت کن.")
        return ConversationHandler.END
    ctx.user_data["calc_materials"] = rows
    ctx.user_data["calc_selected"] = {}
    await send_calc_menu(update.callback_query.message, rows, {})
    return CALC_INPUT

async def send_calc_menu(message, rows, selected):
    txt = "🧮 *محاسبه قیمت محصول*\n\nمقدار هر ماده خام رو وارد کن:\n\n"
    for r in rows:
        qty = selected.get(r["id"], 0)
        txt += f"• {r['name']} ({r['unit']}): *{qty}*\n"
    txt += "\nبرای وارد کردن مقدار بنویس:\n`اسم ماده : مقدار`\nمثلاً: `موم : 50`\n\nوقتی آماده شدی /calculate بزن."
    await message.reply_text(txt, parse_mode="Markdown")

async def calc_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "/calculate":
        return await calc_result(update, ctx)
    try:
        parts = update.message.text.strip().split(":")
        mat_name = parts[0].strip()
        qty = float(parts[1].strip().replace(",", ""))
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ فرمت درست نیست. مثال: `موم : 50`", parse_mode="Markdown")
        return CALC_INPUT
    rows = ctx.user_data["calc_materials"]
    found = next((r for r in rows if r["name"].lower() == mat_name.lower()), None)
    if not found:
        await update.message.reply_text(f"⚠️ ماده «{mat_name}» پیدا نشد. اسم رو دقیق بنویس.")
        return CALC_INPUT
    ctx.user_data["calc_selected"][found["id"]] = qty
    await update.message.reply_text(f"✅ {found['name']}: {qty} {found['unit']} ثبت شد.\n\nادامه بده یا /calculate بزن.")
    return CALC_INPUT

async def calc_result(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    selected = ctx.user_data.get("calc_selected", {})
    rows = ctx.user_data.get("calc_materials", [])
    if not selected:
        await update.message.reply_text("⚠️ هنوز هیچ ماده‌ای وارد نکردی.")
        return CALC_INPUT

    primary_cost = 0
    detail = "📦 *هزینه مواد خام:*\n"
    for r in rows:
        qty = selected.get(r["id"], 0)
        if qty > 0:
            cost = qty * float(r["price_per_unit"])
            primary_cost += cost
            detail += f"• {r['name']}: {qty} {r['unit']} × {float(r['price_per_unit']):,.0f} = *{cost:,.0f} تومان*\n"

    detail += f"\n💰 *جمع هزینه اولیه: {primary_cost:,.0f} تومان*\n"

    sec_rows = supabase.table("secondary_costs").select("*").execute().data
    secondary_cost = 0
    if sec_rows:
        detail += "\n➕ *هزینه‌های ثانویه:*\n"
        for s in sec_rows:
            if s["type"] == "percent":
                amount = primary_cost * float(s["value"]) / 100
                detail += f"• {s['name']} ({s['value']}٪): *{amount:,.0f} تومان*\n"
            else:
                amount = float(s["value"])
                detail += f"• {s['name']}: *{amount:,.0f} تومان*\n"
            secondary_cost += amount

    total = primary_cost + secondary_cost
    detail += f"\n{'═'*25}\n"
    detail += f"🏷 *قیمت نهایی پیشنهادی: {total:,.0f} تومان*"

    await update.message.reply_text(detail, parse_mode="Markdown")
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  لغو
# ═══════════════════════════════════════════════════════════
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    await start(update, ctx)
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════
#  راه‌اندازی
# ═══════════════════════════════════════════════════════════
def main():
    # Health check server در یه thread جداگانه
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(add_mat_start, pattern="^add_mat$")],
        states={
            MAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_name)],
            MAT_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_unit)],
            MAT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_mat_start, pattern="^edit_mat$")],
        states={
            EDIT_MAT_CHOOSE: [CallbackQueryHandler(edit_mat_choose, pattern="^emat_")],
            EDIT_MAT_FIELD: [CallbackQueryHandler(edit_mat_field, pattern="^efield_")],
            EDIT_MAT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_mat_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(add_sec_start, pattern="^add_sec$")],
        states={
            SEC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, sec_name)],
            SEC_TYPE: [CallbackQueryHandler(sec_type, pattern="^stype_")],
            SEC_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sec_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_sec_start, pattern="^edit_sec$")],
        states={
            EDIT_SEC_CHOOSE: [CallbackQueryHandler(edit_sec_choose, pattern="^esec_")],
            EDIT_SEC_FIELD: [CallbackQueryHandler(edit_sec_field, pattern="^sedit_")],
            EDIT_SEC_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_sec_value),
                CallbackQueryHandler(edit_sec_value, pattern="^sntype_")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(calc_start, pattern="^calc$")],
        states={
            CALC_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calc_input),
                CommandHandler("calculate", calc_result)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(CallbackQueryHandler(list_mat, pattern="^list_mat$"))
    app.add_handler(CallbackQueryHandler(list_sec, pattern="^list_sec$"))
    app.add_handler(CallbackQueryHandler(del_mat, pattern="^del_mat$"))
    app.add_handler(CallbackQueryHandler(del_mat_confirm, pattern="^dmat_"))
    app.add_handler(CallbackQueryHandler(del_sec, pattern="^del_sec$"))
    app.add_handler(CallbackQueryHandler(del_sec_confirm, pattern="^dsec_"))
    app.add_handler(CommandHandler("start", start))

    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
