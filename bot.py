import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8637418131:AAGEfmTnwzqtROnN2Rqg2o6oWebO_NNpHkg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ================= DATA =================

group_data = {}
user_data = {}

players = [
    {
        "name": "Virat Kohli",
        "rating": 95,
        "rarity": "Legendary",
        "image": "images/kohli.jpg"
    },
    {
        "name": "MS Dhoni",
        "rating": 93,
        "rarity": "Epic",
        "image": "images/dhoni.jpg"
    }
]

# ================= HELPERS =================

def get_group(group_id):
    if group_id not in group_data:
        group_data[group_id] = {
            "msg_count": 0,
            "drop_at": random.randint(10, 20),
            "active_player": None
        }
    return group_data[group_id]


def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"players": []}
    return user_data[user_id]


# ================= DROP SYSTEM =================

async def drop_player(group_id):
    data = get_group(group_id)
    player = random.choice(players)

    data["active_player"] = player

    await bot.send_photo(
        group_id,
        photo=open(player["image"], "rb"),
        caption="🔥 Guess the player!\nUse /collect <name>"
    )


# ================= MESSAGE HANDLER =================

@dp.message_handler()
async def handle_messages(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    data = get_group(message.chat.id)
    data["msg_count"] += 1

    if data["msg_count"] >= data["drop_at"] and not data["active_player"]:
        await drop_player(message.chat.id)
        data["msg_count"] = 0
        data["drop_at"] = random.randint(10, 20)


# ================= COLLECT =================

@dp.message_handler(commands=["collect"])
async def collect(message: types.Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    data = get_group(group_id)
    player = data["active_player"]

    if not player:
        await message.reply("No active player right now.")
        return

    guess = message.get_args().lower()

    if guess == "":
        await message.reply("Use: /collect player_name")
        return

    if guess in player["name"].lower():
        user = get_user(user_id)
        user["players"].append(player)

        data["active_player"] = None

        await message.reply(
            f"🎉 Correct! You got {player['name']} ({player['rarity']})"
        )
    else:
        await message.reply("❌ Wrong guess!")


# ================= COLLECTION =================

@dp.message_handler(commands=["collection"])
async def collection(message: types.Message):
    user = get_user(message.from_user.id)
    players = user["players"]

    if not players:
        await message.reply("You have no players yet.")
        return

    text = "🏏 Your Collection:\n"
    for p in players:
        text += f"- {p['name']} ({p['rarity']}, {p['rating']})\n"

    await message.reply(text)


# ================= START =================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("🏏 Bot is running! Send messages to spawn players.")


# ================= RUN =================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)