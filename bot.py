import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("BOT_TOKEN"8637418131:AAGEfmTnwzqtROnN2Rqg2o6oWebO_NNpHkg")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

players = [
    {"name": "Virat Kohli", "image": "images/kohli.jpg"},
    {"name": "MS Dhoni", "image": "images/dhoni.jpg"}
]

group_data = {}

def get_group(group_id):
    if group_id not in group_data:
        group_data[group_id] = {
            "msg_count": 0,
            "drop_at": random.randint(10, 20),
            "active_player": None
        }
    return group_data[group_id]


@dp.message()
async def handle_messages(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    data = get_group(message.chat.id)
    data["msg_count"] += 1

    if data["msg_count"] >= data["drop_at"] and not data["active_player"]:
        player = random.choice(players)
        data["active_player"] = player

        await message.answer_photo(
            photo=types.FSInputFile(player["image"]),
            caption="🔥 Guess the player! Use /collect <name>"
        )

        data["msg_count"] = 0
        data["drop_at"] = random.randint(10, 20)


@dp.message(Command("collect"))
async def collect(message: types.Message):
    data = get_group(message.chat.id)
    player = data["active_player"]

    if not player:
        await message.reply("No active player.")
        return

    guess = message.text.split(" ", 1)

    if len(guess) < 2:
        await message.reply("Use: /collect name")
        return

    guess = guess[1].lower()

    if guess in player["name"].lower():
        data["active_player"] = None
        await message.reply(f"🎉 Correct! {player['name']}")
    else:
        await message.reply("❌ Wrong!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
