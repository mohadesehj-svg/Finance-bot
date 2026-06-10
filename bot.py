)reply_markup=InlineKeyboardMarkup(kb ,"چیکار میخوای انجام بدی؟n\.بھ ربات حسابگر مالی خوش اومدیn\ !سلام"

(callback_data="calc")],

] await update.effective_message.reply_text ,"محاسبھ قیمت محصول "(callback_data="del_sec")],

[InlineKeyboardButton ,"حذف ھزینھ ثانویھ "(callback_data="edit_sec"),

InlineKeyboardButton ,"ویرایش ھزینھ ثانویھ "(callback_data="list_sec")],

[InlineKeyboardButton ,"لیست ھزینھھای ثانویھ "(callback_data="add_sec"),

InlineKeyboardButton ,"افزودن ھزینھ ثانویھ "(callback_data="del_mat")],

[InlineKeyboardButton ,"حذف ماده خام "(callback_data="edit_mat"),

InlineKeyboardButton ,"ویرایش ماده خام "(callback_data="list_mat")],

[InlineKeyboardButton ,"لیست مواد خام "(callback_data="add_mat"),

InlineKeyboardButton ,"افزودن ماده خام "(═══════════════════════════════════════════════════════════ async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

kb = [

[InlineKeyboardButton # منوی اصلی — ────────────────────────────────────────── ( MAT_NAME, MAT_UNIT, MAT_PRICE, EDIT_MAT_CHOOSE, EDIT_MAT_FIELD, EDIT_MAT_VALUE, SEC_NAME, SEC_VALUE, SEC_TYPE, EDIT_SEC_CHOOSE, EDIT_SEC_FIELD, EDIT_SEC_VALUE, CALC_INPUT ) = range(13)

# ═══════════════════════════════════════════════════════════ # /start مراحل مکالمھ ─────────────────────────────────────────────── BOT_TOKEN = "8042445672:AAHmBHG2fI08vrdIGnambUfX-S5Pob5egWA" SUPABASE_URL = "https://xnadhiqnrsjgwxvdjwyj.supabase.co" SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhuYWRo

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) logging.basicConfig(level=logging.INFO)

# ─── تنظیمات import os import logging from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import (

Application, CommandHandler, MessageHandler,

CallbackQueryHandler, ConversationHandler, ContextTypes, filters ) from supabase import create_client, Client

# ─── return

)".ھنوز ماده خامی ثبت نشده"(═══════════════════════════════════════════════════════════ async def list_mat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("materials").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # لیست مواد خام # await start(update, ctx) return ConversationHandler.END

# ═══════════════════════════════════════════════════════════ ) "تومان }price:,.0f{ :قیمت ھر واحدctx.user_data['mat_unit']}\n{ :واحد"n\n"

f\!با موفقیت ثبت شد »}]'ctx.user_data['mat_name{« ماده خام "return MAT_PRICE supabase.table("materials").insert({

"name": ctx.user_data["mat_name"],

"unit": ctx.user_data["mat_unit"],

"price_per_unit": price }).execute() await update.message.reply_text(

f

)":لطفا ً فقط عدد وارد کن "(return MAT_PRICE

async def mat_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

try:

price = float(update.message.text.strip().replace(",", "")) except ValueError:

await update.message.reply_text )":قیمت بھ ازای ھر واحد رو بنویس )عدد، بھ تومان("(return MAT_UNIT

async def mat_unit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

ctx.user_data["mat_unit"] = update.message.text.strip() await update.message.reply_text )":واحد اندازهگیری رو بنویس )مثلا ً : گرم، سانتیمتر، عدد("(cancel return MAT_NAME

async def mat_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

ctx.user_data["mat_name"] = update.message.text.strip() await update.message.reply_text/ برای لغو(n\:اسم ماده خام رو بنویس"(═══════════════════════════════════════════════════════════ async def add_mat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() await update.callback_query.message.reply_text # افزودن ماده خام # ═══════════════════════════════════════════════════════════ #

) ]"return EDIT_MAT_VALUE

async def edit_mat_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

field = ctx.user_data["edit_mat_field )

":رو بنویس }]]'await update.callback_query.message.reply_text( f"{labels[ctx.user_data['edit_mat_field }"قیمت جدید )عدد(" :"price" ,"واحد جدید" :"unit" ,"اسم جدید" :"reply_markup=InlineKeyboardMarkup(kb) ) return EDIT_MAT_FIELD

async def edit_mat_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer()

ctx.user_data["edit_mat_field"] = update.callback_query.data.replace("efield_", "")

labels = {"name

,"کدوم فیلد رو ویرایش کنی؟"

(callback_data="efield_price")]

] await update.callback_query.message.reply_text ,"قیمت"(callback_data="efield_unit"),

InlineKeyboardButton ,"واحد"(callback_data="efield_name"),

InlineKeyboardButton ,"اسم"(reply_markup=InlineKeyboardMarkup(kb) ) return EDIT_MAT_CHOOSE

async def edit_mat_choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() mat_id = int(update.callback_query.data.replace("emat_", ""))

ctx.user_data["edit_mat_id"] = mat_id

kb = [

[InlineKeyboardButton ,"کدوم ماده خام رو میخوای ویرایش کنی؟" (return ConversationHandler.END

kb = [[InlineKeyboardButton(r["name"], callback_data=f"emat_{r['id']}")] for r in rows]

await update.callback_query.message.reply_text

)".ھنوز ماده خامی ثبت نشده"(═══════════════════════════════════════════════════════════ async def edit_mat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("materials").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # ویرایش ماده خام # n" await update.callback_query.message.reply_text(txt, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════\تومان }r['unit']}: {float(r['price_per_unit']):,.0f{ ھر — *}]'n\n" for r in rows:

txt += f"• *{r['name\*:لیست مواد خام*

" txt = [ cancel ) return SEC_NAME

async def sec_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

ctx.user_data["sec_name"] = update.message.text.strip()

kb =/ برای لغو(n\n\)مثلا ً : سود، دستمزد، بستھبندی، ارسال(n\:اسم ھزینھ ثانویھ رو بنویس" (═══════════════════════════════════════════════════════════ async def add_sec_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() await update.callback_query.message.reply_text # افزودن ھزینھ ثانویھ # ═══════════════════════════════════════════════════════════ #

)".ماده خام حذف شد "(reply_markup=InlineKeyboardMarkup(kb) )

async def del_mat_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() mat_id = int(update.callback_query.data.replace("dmat_", "")) supabase.table("materials").delete().eq("id", mat_id).execute() await update.callback_query.message.reply_text ,"کدوم ماده خام رو حذف کنی؟" (return

kb = [[InlineKeyboardButton(f" {r['name']}", callback_data=f"dmat_{r['id']}")] for r in

await update.callback_query.message.reply_text

)".ھنوز ماده خامی ثبت نشده"(═══════════════════════════════════════════════════════════ async def del_mat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("materials").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # حذف ماده خام # await start(update, ctx) return ConversationHandler.END

# ═══════════════════════════════════════════════════════════ )"!ماده خام با موفقیت ویرایش شد "(return EDIT_MAT_VALUE supabase.table("materials").update({db_field: val}).eq("id", ctx.user_data["edit_mat_id"] await update.message.reply_text

)":لطفا ً فقط عدد وارد کن "(val = update.message.text.strip().replace(",", "") db_field = "price_per_unit" if field == "price" else field if field == "price":

try:

val = float(val)

except ValueError:

await update.message.reply_text txt += f"• *{r['name']}*: {float(r['value']):,.0f}{t}\n" await update.callback_query.message.reply_text(txt, parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════

"تومان " n\n" for r in rows:

txt = "

t = "٪" if r["type"] == "percent" else\*:ھزینھھای ثانویھ* return

)".ھنوز ھزینھ ثانویھای ثبت نشده"(═══════════════════════════════════════════════════════════ async def list_sec(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("secondary_costs").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # لیست ھزینھھای ثانویھ # val:,.0f} {type_label}" ) await start(update, ctx) return ConversationHandler.END

# ═══════════════════════════════════════════════════════════{ :مقدارn\!ثبت شد »}]'ctx.user_data['sec_name{« ھزینھ "await update.message.reply_text( f

"درصد" if ctx.user_data["sec_type"] == "fixed" else "تومان ثابت" return SEC_VALUE supabase.table("secondary_costs").insert({ "name": ctx.user_data["sec_name"], "value": val, "type": ctx.user_data["sec_type"] }).execute()

type_label = )":لطفا ً فقط عدد وارد کن "(return SEC_VALUE

async def sec_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

try:

val = float(update.message.text.strip().replace(",", "")) except ValueError:

await update.message.reply_text )":رو وارد کن }await update.callback_query.message.reply_text(f"{label صد )مثلا ٢٠ ً برای if ctx.user_data["sec_type"] == "fixed" else "(٪٢٠ "مبلغ )تومان(" reply_markup=InlineKeyboardMar return SEC_TYPE

async def sec_type(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer()

ctx.user_data["sec_type"] = update.callback_query.data.replace("stype_", "")

label = ,":نوع ھزینھ رو انتخاب کن"(callback_data="stype_percent")]

] await update.message.reply_text ,"درصد از ھزینھ اولیھ "(callback_data="stype_fixed"),

InlineKeyboardButton ,"مبلغ ثابت )تومان( "(InlineKeyboardButton[ :return EDIT_SEC_VALUE

async def edit_sec_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

field = ctx.user_data["edit_sec_field"]

if update.callback_query )":رو بنویس }]await update.callback_query.message.reply_text(f"{labels[field }"مقدار جدید )عدد(" :"value" ,"اسم جدید" :"reply_markup else:

labels = {"name ,":نوع جدید رو انتخاب کن"(callback_data="sntype_percent")]

] await update.callback_query.message.reply_text ,"درصد "(callback_data="sntype_fixed"),

InlineKeyboardButton ,"مبلغ ثابت "(reply_markup=InlineKeyboardMarkup(kb) ) return EDIT_SEC_FIELD

async def edit_sec_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() field = update.callback_query.data.replace("sedit_", "")

ctx.user_data["edit_sec_field"] = field

if field == "type":

kb = [

[InlineKeyboardButton

,"کدوم فیلد رو ویرایش کنی؟"

(callback_data="sedit_type")]

] await update.callback_query.message.reply_text ,"نوع"(callback_data="sedit_value"),

InlineKeyboardButton ,"مقدار"(callback_data="sedit_name"),

InlineKeyboardButton ,"اسم"(reply_markup=InlineKeyboardMarkup(kb) ) return EDIT_SEC_CHOOSE

async def edit_sec_choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() ctx.user_data["edit_sec_id"] = int(update.callback_query.data.replace("esec_", ""))

kb = [

[InlineKeyboardButton ,"کدوم ھزینھ رو ویرایش کنی؟" (return ConversationHandler.END

kb = [[InlineKeyboardButton(r["name"], callback_data=f"esec_{r['id']}")] for r in rows]

await update.callback_query.message.reply_text

)".ھنوز ھزینھ ثانویھای ثبت نشده"(═══════════════════════════════════════════════════════════ async def edit_sec_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("secondary_costs").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # ویرایش ھزینھ ثانویھ # return ConversationHandler.END

ctx.user_data["calc_materials"] = rows

)".ابتدا مواد خام رو ثبت کن"(═══════════════════════════════════════════════════════════ async def calc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("materials").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # محاسبھ قیمت محصول # ═══════════════════════════════════════════════════════════ #

)".ھزینھ ثانویھ حذف شد "(reply_markup=InlineKeyboardMarkup(kb) )

async def del_sec_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() sec_id = int(update.callback_query.data.replace("dsec_", "")) supabase.table("secondary_costs").delete().eq("id", sec_id).execute() await update.callback_query.message.reply_text ,"کدوم ھزینھ رو حذف کنی؟" (return

kb = [[InlineKeyboardButton(f" {r['name']}", callback_data=f"dsec_{r['id']}")] for r in

await update.callback_query.message.reply_text

)".ھنوز ھزینھ ثانویھای ثبت نشده"(═══════════════════════════════════════════════════════════ async def del_sec(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.callback_query.answer() rows = supabase.table("secondary_costs").select("*").order("name").execute().data if not rows:

await update.callback_query.message.reply_text # حذف ھزینھ ثانویھ # await start(update, ctx) return ConversationHandler.END

)

# ═══════════════════════════════════════════════════════════ )"!ھزینھ ثانویھ با موفقیت ویرایش شد "(return EDIT_SEC_VALUE supabase.table("secondary_costs").update({field: val}).eq("id", ctx.user_data["edit_sec_i msg = update.callback_query.message if update.callback_query else update.message await msg.reply_text فقط عدد وارد کن "(await update.message.reply_text

":لطفا await update.callback_query.answer() val = update.callback_query.data.replace("sntype_", "") else:

val = update.message.text.strip().replace(",", "")

if field == "value":

try:

val = float(val)

except ValueError:

ً }n" for r in rows:

qty = selected.get(r["id"], 0)

if qty > 0:

cost = qty * float(r["price_per_unit"])

primary_cost += cost detail += f"• {r['name']}: {qty} {r['unit']} × {float(r['price_per_unit']):,.0f\*:ھزینھ مواد خام* " primary_cost = 0 detail = ھزینھ اولیھ #

return CALC_INPUT

)".ھنوز ھیچ مادهای وارد نکردی "(async def calc_result(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

selected = ctx.user_data.get("calc_selected", {}) rows = ctx.user_data.get("calc_materials", []) if not selected:

await update.message.reply_text

یاn\n\.ثبت شد }]'return CALC_INPUT

ctx.user_data["calc_selected"][found["id"]] = qty

await update.message.reply_text(f" return CALC_INPUT

{found['name']}: {qty} {found['unit )".پیدا نشد. اسم رو دقیق بنویس »}mat_name{« ماده "`", parse_mode="Ma return CALC_INPUT

rows = ctx.user_data["calc_materials"]

found = next((r for r in rows if r["name"].lower() == mat_name.lower()), None) if not found:

await update.message.reply_text(fفرمت درست نیست. مثال: `موم : await message.reply_text(txt, parse_mode="Markdown")

async def calc_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

if update.message.text.strip() == "/calculate":

return await calc_result(update, ctx) try:

parts = update.message.text.strip().split(":") mat_name = parts[0].strip() qty = float(parts[1].strip().replace(",", "")) except (ValueError, IndexError):

await update.message.reply_text(" 50

ی آماده شدی`\n\nمثلا ` : ًموم : `\n50اسم ماده : مقدارn`\:برای وارد کردن مقدار بنویسn\n"

for r in rows:

qty = selected.get(r["id"], 0)

txt += f"• {r['name']} ({r['unit']}): *{qty}*\n" txt += "\n\:مقدار ھر ماده خام رو وارد کنn\n\*محاسبھ قیمت محصول*

" ctx.user_data["calc_selected"] = {}

await send_calc_menu(update.callback_query.message, rows, {}) return CALC_INPUT

async def send_calc_menu(message, rows, selected):

txt = ,} ,])app.add_handler(ConversationHandler(

entry_points=[CallbackQueryHandler(add_mat_start, pattern="^add_mat$")], states={

MAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_name)],

MAT_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_unit)],

MAT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_price افزودن ماده خام :═══════════════════════════════════════════════════════════ def main():

app = Application.builder().token(BOT_TOKEN).build()

# Conversation # راهاندازی # await start(update, ctx)

return ConversationHandler.END

# ═══════════════════════════════════════════════════════════

)".عملیات لغو شد "(═══════════════════════════════════════════════════════════ async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text # لغو # await update.message.reply_text(detail, parse_mode="Markdown")

await start(update, ctx) return ConversationHandler.END

# ═══════════════════════════════════════════════════════════

"*تومان }total:,.0f{ :قیمت نھایی پیشنھادی* "n" secondary_cost += amount

total = primary_cost + secondary_cost detail += f"\n{'═'*25}\n" detail += f\*تومان }n" else:

amount = float(s["value"])

detail += f"• {s['name']}: *{amount:,.0f\*تومان }n" for s in sec_rows:

if s["type"] == "percent":

amount = primary_cost * float(s["value"]) / 100

detail += f"• {s['name']} ({s['value']}٪): *{amount:,.0f\*:ھزینھھای ثانویھ* sec_rows = supabase.table("secondary_costs").select("*").execute().data secondary_cost = 0 if sec_rows:

detail += "\n ھزینھھای ثانویھ #

"n\*تومان }primary_cost:,.0f{ :جمع ھزینھ اولیھ*

detail += f"\n ,] )app.add_handler(ConversationHandler(

entry_points=[CallbackQueryHandler(calc_start, pattern="^calc$")], states={ CALC_INPUT: [ MessageHandler(filters.TEXT & ~filters.COMMAND, calc_input), CommandHandler("calculate", calc_result محاسبھ :app.add_handler(ConversationHandler(

entry_points=[CallbackQueryHandler(edit_sec_start, pattern="^edit_sec$")], states={

EDIT_SEC_CHOOSE: [CallbackQueryHandler(edit_sec_choose, pattern="^esec_")],

EDIT_SEC_FIELD: [CallbackQueryHandler(edit_sec_field, pattern="^sedit_")],

EDIT_SEC_VALUE: [ MessageHandler(filters.TEXT & ~filters.COMMAND, edit_sec_value), CallbackQueryHandler(edit_sec_value, pattern="^sntype_") ],

}, fallbacks=[CommandHandler("cancel", cancel)]

))

# Conversation ویرایش ھزینھ ثانویھ :app.add_handler(ConversationHandler(

entry_points=[CallbackQueryHandler(add_sec_start, pattern="^add_sec$")], states={ SEC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, sec_name)],

SEC_TYPE: [CallbackQueryHandler(sec_type, pattern="^stype_")],

SEC_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sec_value)],

}, fallbacks=[CommandHandler("cancel", cancel)]

))

# Conversation افزودن ھزینھ ثانویھ :app.add_handler(ConversationHandler(

entry_points=[CallbackQueryHandler(edit_mat_start, pattern="^edit_mat$")], states={

EDIT_MAT_CHOOSE: [CallbackQueryHandler(edit_mat_choose, pattern="^emat_")],

EDIT_MAT_FIELD: [CallbackQueryHandler(edit_mat_field, pattern="^efield_")],

EDIT_MAT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_mat_value)]

}, fallbacks=[CommandHandler("cancel", cancel)]

))

# Conversation ویرایش ماده خام :fallbacks=[CommandHandler("cancel", cancel)]

))

# Conversation )(app.run_polling()

if __name__ == "__main__":

main )"...ربات در حال اجراست "(app.add_handler(CallbackQueryHandler(list_mat, pattern="^list_mat$")) app.add_handler(CallbackQueryHandler(list_sec, pattern="^list_sec$")) app.add_handler(CallbackQueryHandler(del_mat, pattern="^del_mat$")) app.add_handler(CallbackQueryHandler(del_mat_confirm, pattern="^dmat_")) app.add_handler(CallbackQueryHandler(del_sec, pattern="^del_sec$")) app.add_handler(CallbackQueryHandler(del_sec_confirm, pattern="^dsec_"))

app.add_handler(CommandHandler("start", start))

print ھای ساده fallbacks=[CommandHandler("cancel", cancel)]

))

# Callback ,}
