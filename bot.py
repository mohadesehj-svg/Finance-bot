import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from supabase import create_client, Client

BOT_TOKEN = "8042445672:AAF4WeGyQkk25obz6vvyBtvKubmN5hxH5g0"
SUPABASE_URL = "https://xnadhiqnrsjgwxvdjwyj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhuYWRoaXFucnNqZ3d4dmRqd3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEwNzcyNzksImV4cCI6MjA5NjY1MzI3OX0.BYqP768Ns5htizmjOU_3L3sQ8S7hCJbciFoP0reuM9U"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(level=logging.INFO)

# state هر کاربر
user_state = {}

# ─── Health Check ───────────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

# ─── منوی اصلی ─────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ افزودن ماده خام", callback_data="add_mat"),
         InlineKeyboardButton("📋 لیست مواد خام", callback_data="list_mat")],
        [InlineKeyboardButton("✏️ ویرایش ماده خام", callback_data="edit_mat"),
         InlineKeyboardButton("🗑 حذف ماده خام", callback_data="del_mat")],
        [InlineKeyboardButton("➕ افزودن هزینه ثانویه", callback_data="add_sec"),
         InlineKeyboardButton("📋 لیست هزینه‌های ثانویه", callback_data="list_sec")],
        [InlineKeyboardButton("✏️ ویرایش هزینه ثانویه", callback_data="edit_sec"),
         InlineKeyboardButton("🗑 حذف هزینه ثانویه", callback_data="del_sec")],
        [InlineKeyboardButton("🧮 محاسبه قیمت محصول", callback_data="calc")],
    ])

async def show_menu(msg):
    await msg.reply_text("چیکار می‌خوای انجام بدی؟", reply_markup=main_menu_kb())

# ─── /start ────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_state[uid] = {"step": None}
    await update.message.reply_text("سلام! 👋 به ربات حسابگر مالی خوش اومدی.", reply_markup=main_menu_kb())

# ─── پردازش پیام متنی ──────────────────────────────────────
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    state = user_state.get(uid, {})
    step = state.get("step")

    # ── افزودن ماده خام ──
    if step == "mat_name":
        user_state[uid]["mat_name"] = text
        user_state[uid]["step"] = "mat_unit"
        await update.message.reply_text("واحد اندازه‌گیری رو بنویس (مثلاً: گرم، سانتیمتر، عدد):")

    elif step == "mat_unit":
        user_state[uid]["mat_unit"] = text
        user_state[uid]["step"] = "mat_price"
        await update.message.reply_text("قیمت به ازای هر واحد رو بنویس (عدد، به تومان):")

    elif step == "mat_price":
        try:
            price = float(text.replace(",", ""))
        except ValueError:
            await update.message.reply_text("⚠️ فقط عدد وارد کن:")
            return
        supabase.table("materials").insert({
            "name": user_state[uid]["mat_name"],
            "unit": user_state[uid]["mat_unit"],
            "price_per_unit": price
        }).execute()
        await update.message.reply_text(
            f"✅ ماده خام «{user_state[uid]['mat_name']}» ثبت شد!\n"
            f"واحد: {user_state[uid]['mat_unit']}\nقیمت هر واحد: {price:,.0f} تومان"
        )
        user_state[uid] = {"step": None}
        await show_menu(update.message)

    # ── ویرایش ماده خام ──
    elif step == "edit_mat_value":
        field = state["edit_field"]
        db_field = "price_per_unit" if field == "price" else field
        val = text.replace(",", "")
        if field == "price":
            try:
                val = float(val)
            except ValueError:
                await update.message.reply_text("⚠️ فقط عدد وارد کن:")
                return
        supabase.table("materials").update({db_field: val}).eq("id", state["edit_id"]).execute()
        await update.message.reply_text("✅ ماده خام ویرایش شد!")
        user_state[uid] = {"step": None}
        await show_menu(update.message)

    # ── افزودن هزینه ثانویه ──
    elif step == "sec_name":
        user_state[uid]["sec_name"] = text
        user_state[uid]["step"] = "sec_type"
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("💰 مبلغ ثابت (تومان)", callback_data="stype_fixed"),
            InlineKeyboardButton("📊 درصد از هزینه اولیه", callback_data="stype_percent")
        ]])
        await update.message.reply_text("نوع هزینه رو انتخاب کن:", reply_markup=kb)

    elif step == "sec_value":
        try:
            val = float(text.replace(",", ""))
        except ValueError:
            await update.message.reply_text("⚠️ فقط عدد وارد کن:")
            return
        supabase.table("secondary_costs").insert({
            "name": user_state[uid]["sec_name"],
            "value": val,
            "type": user_state[uid]["sec_type"]
        }).execute()
        type_label = "تومان ثابت" if user_state[uid]["sec_type"] == "fixed" else "درصد"
        await update.message.reply_text(
            f"✅ هزینه «{user_state[uid]['sec_name']}» ثبت شد!\nمقدار: {val:,.0f} {type_label}"
        )
        user_state[uid] = {"step": None}
        await show_menu(update.message)

    # ── ویرایش هزینه ثانویه ──
    elif step == "edit_sec_value":
        field = state["edit_field"]
        val = text.replace(",", "")
        if field == "value":
            try:
                val = float(val)
            except ValueError:
                await update.message.reply_text("⚠️ فقط عدد وارد کن:")
                return
        supabase.table("secondary_costs").update({field: val}).eq("id", state["edit_id"]).execute()
        await update.message.reply_text("✅ هزینه ثانویه ویرایش شد!")
        user_state[uid] = {"step": None}
        await show_menu(update.message)

    # ── محاسبه ──
    elif step == "calc":
        if text == "/calculate":
            await do_calculate(update, uid)
            return
        try:
            parts = text.split(":")
            mat_name = parts[0].strip()
            qty = float(parts[1].strip().replace(",", ""))
        except (ValueError, IndexError):
            await update.message.reply_text("⚠️ فرمت درست نیست. مثال:\nموم : 50")
            return
        rows = state.get("calc_materials", [])
        found = next((r for r in rows if r["name"].strip() == mat_name.strip()), None)
        if not found:
            names = "\n".join([f"• {r['name']}" for r in rows])
            await update.message.reply_text(f"⚠️ ماده «{mat_name}» پیدا نشد.\nمواد موجود:\n{names}")
            return
        user_state[uid]["calc_selected"][found["id"]] = qty
        await update.message.reply_text(
            f"✅ {found['name']}: {qty} {found['unit']} ثبت شد.\n\nماده دیگه‌ای داری؟ وارد کن یا /calculate بزن."
        )

    else:
        await show_menu(update.message)

# ─── محاسبه نهایی ──────────────────────────────────────────
async def do_calculate(update, uid):
    state = user_state.get(uid, {})
    selected = state.get("calc_selected", {})
    rows = state.get("calc_materials", [])

    if not selected:
        await update.message.reply_text("⚠️ هنوز هیچ ماده‌ای وارد نکردی.")
        return

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
    detail += f"\n{'═'*25}\n🏷 *قیمت نهایی: {total:,.0f} تومان*"

    await update.message.reply_text(detail, parse_mode="Markdown")
    user_state[uid] = {"step": None}
    await show_menu(update.message)

# ─── پردازش دکمه‌ها ────────────────────────────────────────
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    # ── افزودن ماده خام ──
    if data == "add_mat":
        user_state[uid] = {"step": "mat_name"}
        await q.message.reply_text("اسم ماده خام رو بنویس:")

    # ── لیست مواد خام ──
    elif data == "list_mat":
        rows = supabase.table("materials").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز ماده خامی ثبت نشده.")
            return
        txt = "📋 *لیست مواد خام:*\n\n"
        for r in rows:
            txt += f"• *{r['name']}* — هر {r['unit']}: {float(r['price_per_unit']):,.0f} تومان\n"
        await q.message.reply_text(txt, parse_mode="Markdown")

    # ── ویرایش ماده خام ──
    elif data == "edit_mat":
        rows = supabase.table("materials").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز ماده خامی ثبت نشده.")
            return
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(r["name"], callback_data=f"emat_{r['id']}")] for r in rows])
        await q.message.reply_text("کدوم ماده خام رو ویرایش کنی؟", reply_markup=kb)

    elif data.startswith("emat_"):
        mat_id = int(data.replace("emat_", ""))
        user_state[uid] = {"step": "edit_mat_choose", "edit_id": mat_id}
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("اسم", callback_data="efield_name"),
            InlineKeyboardButton("واحد", callback_data="efield_unit"),
            InlineKeyboardButton("قیمت", callback_data="efield_price")
        ]])
        await q.message.reply_text("کدوم فیلد رو ویرایش کنی؟", reply_markup=kb)

    elif data.startswith("efield_"):
        field = data.replace("efield_", "")
        user_state[uid]["edit_field"] = field
        user_state[uid]["step"] = "edit_mat_value"
        labels = {"name": "اسم جدید", "unit": "واحد جدید", "price": "قیمت جدید (عدد)"}
        await q.message.reply_text(f"{labels[field]} رو بنویس:")

    # ── حذف ماده خام ──
    elif data == "del_mat":
        rows = supabase.table("materials").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز ماده خامی ثبت نشده.")
            return
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"🗑 {r['name']}", callback_data=f"dmat_{r['id']}")] for r in rows])
        await q.message.reply_text("کدوم ماده خام رو حذف کنی؟", reply_markup=kb)

    elif data.startswith("dmat_"):
        mat_id = int(data.replace("dmat_", ""))
        supabase.table("materials").delete().eq("id", mat_id).execute()
        await q.message.reply_text("✅ ماده خام حذف شد.")

    # ── افزودن هزینه ثانویه ──
    elif data == "add_sec":
        user_state[uid] = {"step": "sec_name"}
        await q.message.reply_text("اسم هزینه ثانویه رو بنویس:\n(مثلاً: سود، دستمزد، بسته‌بندی، ارسال)")

    elif data.startswith("stype_"):
        user_state[uid]["sec_type"] = data.replace("stype_", "")
        user_state[uid]["step"] = "sec_value"
        label = "مبلغ (تومان)" if user_state[uid]["sec_type"] == "fixed" else "درصد (مثلاً ۲۰ برای ۲۰٪)"
        await q.message.reply_text(f"{label} رو وارد کن:")

    # ── لیست هزینه‌های ثانویه ──
    elif data == "list_sec":
        rows = supabase.table("secondary_costs").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
            return
        txt = "📋 *هزینه‌های ثانویه:*\n\n"
        for r in rows:
            t = "٪" if r["type"] == "percent" else " تومان"
            txt += f"• *{r['name']}*: {float(r['value']):,.0f}{t}\n"
        await q.message.reply_text(txt, parse_mode="Markdown")

    # ── ویرایش هزینه ثانویه ──
    elif data == "edit_sec":
        rows = supabase.table("secondary_costs").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
            return
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(r["name"], callback_data=f"esec_{r['id']}")] for r in rows])
        await q.message.reply_text("کدوم هزینه رو ویرایش کنی؟", reply_markup=kb)

    elif data.startswith("esec_"):
        sec_id = int(data.replace("esec_", ""))
        user_state[uid] = {"step": "edit_sec_choose", "edit_id": sec_id}
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("اسم", callback_data="sedit_name"),
            InlineKeyboardButton("مقدار", callback_data="sedit_value"),
        ]])
        await q.message.reply_text("کدوم فیلد رو ویرایش کنی؟", reply_markup=kb)

    elif data.startswith("sedit_"):
        field = data.replace("sedit_", "")
        user_state[uid]["edit_field"] = field
        user_state[uid]["step"] = "edit_sec_value"
        labels = {"name": "اسم جدید", "value": "مقدار جدید (عدد)"}
        await q.message.reply_text(f"{labels[field]} رو بنویس:")

    # ── حذف هزینه ثانویه ──
    elif data == "del_sec":
        rows = supabase.table("secondary_costs").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("هنوز هزینه ثانویه‌ای ثبت نشده.")
            return
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"🗑 {r['name']}", callback_data=f"dsec_{r['id']}")] for r in rows])
        await q.message.reply_text("کدوم هزینه رو حذف کنی؟", reply_markup=kb)

    elif data.startswith("dsec_"):
        sec_id = int(data.replace("dsec_", ""))
        supabase.table("secondary_costs").delete().eq("id", sec_id).execute()
        await q.message.reply_text("✅ هزینه ثانویه حذف شد.")

    # ── محاسبه ──
    elif data == "calc":
        rows = supabase.table("materials").select("*").order("name").execute().data
        if not rows:
            await q.message.reply_text("ابتدا مواد خام رو ثبت کن.")
            return
        user_state[uid] = {"step": "calc", "calc_materials": rows, "calc_selected": {}}
        names = "\n".join([f"• {r['name']} ({r['unit']})" for r in rows])
        await q.message.reply_text(
            f"🧮 *محاسبه قیمت محصول*\n\nمواد موجود:\n{names}\n\n"
            "برای هر ماده بنویس:\n`اسم ماده : مقدار`\nمثلاً: `موم : 50`\n\n"
            "وقتی تموم شد /calculate بزن.",
            parse_mode="Markdown"
        )

# ─── راه‌اندازی ────────────────────────────────────────────
def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calculate", lambda u, c: do_calculate(u, u.effective_user.id)))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
