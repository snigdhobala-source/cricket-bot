import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8637418131:AAGEfmTnwzqtROnN2Rqg2o6oWebO_NNpHkg"

matches = {}

def get_outcome(power=False):
    if power:
        outcomes = ["0","1","4","6","W"]
        weights = [10,15,25,20,25]
    else:
        outcomes = ["0","1","2","4","6","W"]
        weights = [20,30,20,15,5,10]
    return random.choices(outcomes, weights)[0]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏏 Welcome!\nUse /play")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    matches[user_id] = {"runs":0,"balls":0,"wickets":0}

    keyboard = [[
        InlineKeyboardButton("Normal", callback_data="normal"),
        InlineKeyboardButton("Power 💥", callback_data="power")
    ]]

    await update.message.reply_text(
        "Match Started (5 overs)\nChoose shot:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    match = matches.get(user_id)

    if not match:
        await query.edit_message_text("Use /play first")
        return

    if match["balls"] >= 30 or match["wickets"] >= 3:
        await query.edit_message_text(
            f"Match Over!\nScore: {match['runs']}/{match['wickets']}"
        )
        return

    outcome = get_outcome(query.data == "power")
    match["balls"] += 1

    if outcome == "W":
        match["wickets"] += 1
        text = "WICKET ❌"
    else:
        match["runs"] += int(outcome)
        text = f"Scored {outcome} runs"

    keyboard = [[
        InlineKeyboardButton("Normal", callback_data="normal"),
        InlineKeyboardButton("Power 💥", callback_data="power")
    ]]

    await query.edit_message_text(
        f"{text}\n\nScore: {match['runs']}/{match['wickets']}\nBalls: {match['balls']}/30",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CallbackQueryHandler(handle))

app.run_polling()