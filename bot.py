import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from PIL import Image, ImageFilter

API_TOKEN = "8637418131:AAGEfmTnwzqtROnN2Rqg2o6oWebO_NNpHkg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ================== DATA ==================

group_data = {}
user_data = {}
user_cooldowns = {}

players = [
    {"name": "Virat Kohli", "rating": 95, "rarity": "Legendary", "image": "kohli.jpg"},
    {"name": "MS Dhoni", "rating": 93, "rarity": "Epic", "image": "dhoni.jpg"},
    {"name": "Rohit Sharma", "rating": 92, "rarity": "Epic", "image": "rohit.jpg"},
    {"name": "Hardik Pandya", "rating": 89, "rarity": "Rare", "image": "hardik.jpg"},
    {"name": "Shubman Gill", "rating": 90, "rarity": "Rare", "image": "gill.jpg"}
]

# ================== UTIL ==================

def get_group(group_id):
    if group_id not in group_data:
        group_data[group_id] = {
            "msg_count": 0,
            "drop_at": random.randint(20, 50),
            "active_player": None
        }
    return group_data[group_id]


def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"players": []}
    return user_data[user_id]


def get_random_player():
    roll = random.randint(1, 100)

    if roll <= 50:
        rarity = "Common"
    elif roll <= 80:
        rarity = "Rare"
    elif roll <= 95:
        rarity = "Epic"
    else:
        rarity = "Legendary"

    filtered = [p for p in players if p["rarity"] == rarity]
    if not filtered:
        filtered = players

    return random.choice(filtered)


def blur_image(input_path, output_path):
    img = Image.open(input_path)
    blurred = img.filter(ImageFilter.GaussianBlur(10))
    blurred.save(output_path)


# ================== DROP SYSTEM ==================

async def drop_player(group_id):
    data = get_group(group_id)
    player = get_random_player()
    data["active_player"] = player

    blur_image(player["image"], "blur.jpg")

    await bot.send_photo(
        group_id,
        photo=open("blur.jpg", "rb"),
        caption="🔥 Guess the player!\nUse /collect <name>"
    )


# ================== MESSAGE HANDLER ==================

@dp.message_handler()
async def handle_messages(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    data = get_group(message.chat.id)
    data["msg_count"] += 1

    if data["msg_count"] >= data["drop_at"] and not data["active_player"]:
        await drop_player(message.chat.id)
        data["msg_count"] = 0
        data["drop_at"] = random.randint(20, 50)


# ================== COLLECT ==================

@dp.message_handler(commands=["collect"])
async def collect(message: Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    data = get_group(group_id)
    player = data["active_player"]

    if not player:
        await message.reply("No active player right now.")
        return

    args = message.get_args()
    if not args:
        await message.reply("Usage: /collect <player name>")
        return

    guess = args.lower()

    # cooldown
    if user_id in user_cooldowns:
        await message.reply("⏳ Wait before guessing again!")
        return

    if guess in player["name"].lower():
        user = get_user(user_id)
        user["players"].append(player)

        data["active_player"] = None

        await message.reply(
            f"🎉 Correct!\nYou got {player['name']} ({player['rarity']}, {player['rating']})"
        )
    else:
        user_cooldowns[user_id] = True
        await message.reply("❌ Wrong guess!")

        await asyncio.sleep(10)
        user_cooldowns.pop(user_id, None)


# ================== COLLECTION ==================

@dp.message_handler(commands=["collection"])
async def collection(message: Message):
    user = get_user(message.from_user.id)
    players = user["players"]

    if not players:
        await message.reply("You have no players.")
        return

    text = "🏏 Your Collection:\n"
    for p in players:
        text += f"- {p['name']} ({p['rarity']}, {p['rating']})\n"

    await message.reply(text)


# ================== START ==================

@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("🏏 Cricket Collector Bot Started!\nChat to spawn players!")


# ================== RUN ==================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
