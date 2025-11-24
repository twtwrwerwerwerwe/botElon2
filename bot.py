import asyncio
import logging
import random
import os
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from telethon import TelegramClient
from telethon.errors import FloodWaitError

# ================= CONFIG =================
TOKEN = "8285781260:AAE3Oq6ZyCrPHeaSvMJjZiV7Q3xChHEMlVc"
ADMIN_ID = 6302873072

API_ID = 32460736
API_HASH = "285e2a8556652e6f4ffdb83658081031"
SESSION_NAME = "session"

# Kanallar ro‘yxati (faqat yuboriladi, join YO‘Q)
TARGETS = [
    "https://t.me/BUVAYDA_YANGIQORGON_Toshkentt",
    "https://t.me/taxi_bogdod_toshkent_rishton",
    "https://t.me/bogdod_toshken_taksi",
    "https://t.me/bogdod1_toshkent",
    "https://t.me/bogdod_rishton_toshken_taksi",
    "https://t.me/Bogdod_toshkent_yangiqorgonbuvay",
    "https://t.me/buvayda_bagdod8",
    "https://t.me/Buvayda_Bogdod_Toshkent",
    "https://t.me/Toshkent_zodyon_beshkapa",
    "https://t.me/taxi_bogdod_toshken",
    "https://t.me/rishron_toshkent_rishton",
    "https://t.me/buvayda_toshkent_buvayda_taxi",
    "https://t.me/toshkent_uyrat_dormancha",
    3292352387,
    2558743974,
    "https://t.me/taxi_toshkent_bogdod",
    "https://t.me/Toshkent_bogdod_buvayda_taksi",
    "https://t.me/Bogdod_toshkent_rishton_taxil",
    "https://t.me/toshkent_rishton_bogdod_taksi",
    "https://t.me/bogdod_toshkent_rishton2",
    "https://t.me/buvayda_toshkent_rishton",
    "https://t.me/toshkent_bogdod_rishton_buvayd",
    "https://t.me/toshkenbogdodd",
    "https://t.me/buvayda_toshkentttt",
    "https://t.me/bagdod_toshkent_ta",
    "https://t.me/bagdod_toshkent88888",
    "https://t.me/buvayda_rishton_qoqon_taksi",
    "https://t.me/shafyorlar_toshken_buvaydabogdod",
    "https://t.me/rishton_toshkent_taksil",
    "https://t.me/Rishton_Buvayda_Toshkent_Bogdodi",
    "https://t.me/bogdod_toshkent_33",
    "https://t.me/toshkentbag",
    "https://t.me/Rishton_Buvayda_Toshkent_Bogdod",
    "https://t.me/sox_rishton",
    "https://t.me/buvayda_bagdod9",
    "https://t.me/bagdod_1",
    "https://t.me/Toshken_Bogdod_Bogdod_Toshkent",
    "https://t.me/rishton_bogdod_toshken_taxi",
    "https://t.me/Buvayda_toshkent_yangiqorgonn",
    "https://t.me/Toshkent_Bogdod",
    "https://t.me/Toshkent_Bagdod_toshken",
    "https://t.me/buvayda_toshkent_taksi2",
    "https://t.me/buvayda_toshkent_bogdod_toshkent",
    "https://t.me/rishton_toshkent_taksi_7",
    "https://t.me/Toshkent_Rishton",
    "https://t.me/toshkent_buvayda_bagdodd",
    "https://t.me/toshken_rishton",
    "https://t.me/BogdodToshkent2023",
    "https://t.me/Bagdod_Toshkent_taxilar_taksila",
    "https://t.me/toshkent_bogdod_toshkent_taksi",
    "https://t.me/bagdod_rishton_qoqon_toshkent",
    "https://t.me/bogdod_toshkent_shafyorlar",
    "https://t.me/toshkent_bogdod_taxi",
    "https://t.me/rishton_toshkent_bogdod_n1",
    "https://t.me/bogdod_toshkent_rishton1",
    "https://t.me/toshkentrishtonbagdod",
    "https://t.me/Toshkent_Rishton_258",
    "https://t.me/taxichen",
    "https://t.me/taksi_toshkent_rishton",
    "https://t.me/Rishton_Toshkent2",
    "https://t.me/rishton_toshkent_bogdod_bagdod",
    "https://t.me/Toshkent_Fargona_taxis",
    "https://t.me/Rishton_Toshkenttaksilari",
    "https://t.me/Toshkent_Rishton24",
    "https://t.me/Toshkent_oltiariq_rishton_Bagdot",
    "https://t.me/Rishton_Toshken_7",
    "https://t.me/bagdod_buvayda0",
    "https://t.me/RishtonBagdodToshkent",
    "https://t.me/toshkent_rishton_taxi",
    "https://t.me/Rishton_Toshkent_11",
    "https://t.me/RishtonToshkenttaxiii",
    "https://t.me/Rishton_Toshkent_Rishton",
    "https://t.me/Rishton_Bogdod_Toshkent_taksii",
    "https://t.me/Bogdodtoshkenttaksi1",
    "https://t.me/rishton_toshkent_1",
    "https://t.me/Rishton_bogdodToshkent",
    "https://t.me/RishtanTashkent",
    "https://t.me/Toshkent_Yangiqorgon_taxi",
    "https://t.me/Rishton_Toshkent_T",
    "https://t.me/rishton_oltiariq_bogdod_metan",
    "https://t.me/RishtonToshkenttaksi",
    "https://t.me/Yangiqurgon_Namangan_Toshkent",
    "https://t.me/pitagkr",
    "https://t.me/bagdod_rishton_toshkent_qoqon",
    "https://t.me/rishton_toshkent_24",
    "https://t.me/Rishton_Toshkent_taksii",
    "https://t.me/zarafshontoshkenttaksi",
    "https://t.me/Bagdod_Toshken",
    "https://t.me/TOSHKENT_RISHTON_TAXI_745",
    "https://t.me/fargona_oltiariq_taxi_n1",
    "https://t.me/Rishton_Toshkent_taxi",
    "https://t.me/RishtonToshent",
    4995617733,
    "https://t.me/RishtonToshkentTaxii",
    "https://t.me/ToshkentRishtonTaxi",
    5003347692,
    "https://t.me/bogdod_rishton_toshkent",
    1948039973
]

# Aiogram init
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Telethon init
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

sending_tasks = {}
approved_users = set()

# ================= KEYBOARDS =================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📢 E’lon yuborish")]],
        resize_keyboard=True
    )

def back_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Orqaga")]],
        resize_keyboard=True
    )

def interval_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="5 daqiqa", callback_data="interval_5")],
            [InlineKeyboardButton(text="7 daqiqa", callback_data="interval_7")],
            [InlineKeyboardButton(text="10 daqiqa", callback_data="interval_10")],
            [InlineKeyboardButton(text="15 daqiqa", callback_data="interval_15")],
        ]
    )

# ================= START =================
@dp.message(CommandStart())
async def start_cmd(message: Message):
    uid = message.from_user.id
    if uid in approved_users:
        return await message.answer("👋 Xush kelibsiz!", reply_markup=main_menu())
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📨 So‘rov yuborish", callback_data=f"request_{uid}")]]
    )
    await message.answer("🛑 Botdan foydalanish uchun ruxsat kerak.", reply_markup=markup)

@dp.callback_query(F.data.startswith("request_"))
async def request_access(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])
    u = call.from_user

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ruxsat", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"deny_{user_id}")
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        f"👤 <b>{u.full_name}</b>\nID: <code>{user_id}</code>",
        reply_markup=markup
    )
    await call.message.edit_text("📨 So‘rov yuborildi.")

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])
    approved_users.add(user_id)
    await bot.send_message(user_id, "✅ Ruxsat berildi!", reply_markup=main_menu())
    await call.message.edit_text("Ruxsat berildi.")

@dp.callback_query(F.data.startswith("deny_"))
async def deny(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await bot.send_message(user_id, "❌ So‘rov rad qilindi.")
    await call.message.edit_text("Rad qilindi.")

# ================= E’LON BOSHLASH =================
@dp.message(F.text == "📢 E’lon yuborish")
async def elon_start(message: Message):
    uid = message.from_user.id
    if uid not in approved_users:
        return await message.answer("🛑 Sizda ruxsat yo‘q.")
    await dp.storage.set_state(uid, "elon_text")
    await message.answer("✍️ Matn kiriting:", reply_markup=back_button())

@dp.message(F.text == "◀️ Orqaga")
async def back(message: Message):
    await dp.storage.set_state(message.from_user.id, None)
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())

@dp.message(F.text)
async def get_text(message: Message):
    uid = message.from_user.id
    state = await dp.storage.get_state(uid)
    if state != "elon_text":
        return
    await dp.storage.update_data(uid, {"text": message.text})
    await dp.storage.set_state(uid, "elon_photo")
    await message.answer("🖼 Rasm yuboring:")

@dp.message(F.photo)
async def get_photo(message: Message):
    uid = message.from_user.id
    state = await dp.storage.get_state(uid)
    if state != "elon_photo":
        return
    photo_id = message.photo[-1].file_id
    data = await dp.storage.get_data(uid)
    data["photo"] = photo_id
    await dp.storage.update_data(uid, data)
    await dp.storage.set_state(uid, "interval")
    await message.answer("⏱ Intervalni tanlang:", reply_markup=interval_buttons())

# ================= INTERVAL =================
@dp.callback_query(F.data.startswith("interval_"))
async def choose_interval(call: CallbackQuery):
    interval = int(call.data.split("_")[1])
    uid = call.from_user.id

    data = await dp.storage.get_data(uid)
    text = data["text"]
    photo = data["photo"]

    await call.message.edit_text("📨 Jo‘natish boshlandi!")
    await bot.send_message(uid, "🟢 Yuborilmoqda...", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛑 To‘xtatish")]],
        resize_keyboard=True
    ))

    task = asyncio.create_task(send_loop(uid, text, photo, interval))
    sending_tasks[uid] = task

# ================= SEND LOOP =================
async def send_loop(uid: int, text: str, photo_file_id: str, interval: int):
    await client.start()

    os.makedirs("temp_media", exist_ok=True)
    local_path = f"temp_media/{photo_file_id.replace('/', '_')}.jpg"
    await bot.download(photo_file_id, local_path)

    end = datetime.now() + timedelta(hours=24)

    while datetime.now() < end:
        for target in TARGETS:
            try:
                entity = await client.get_entity(target)
                await client.send_file(entity, local_path, caption=text)
                await bot.send_message(uid, f"✅ Yuborildi: {target}")
                await asyncio.sleep(random.uniform(1.0, 2.0))
            except FloodWaitError as fw:
                await bot.send_message(uid, f"⏳ FloodWait {fw.seconds}s → {target}")
                await asyncio.sleep(fw.seconds + 1)
            except Exception as e:
                await bot.send_message(uid, f"⚠️ Xato: {target}\n{e}")

        await asyncio.sleep(interval * 60)

    if os.path.exists(local_path):
        os.remove(local_path)

    await bot.send_message(uid, "⏰ 24 soat tugadi.", reply_markup=main_menu())
    sending_tasks.pop(uid, None)

# ================= STOP =================
@dp.message(F.text == "🛑 To‘xtatish")
async def stop(message: Message):
    uid = message.from_user.id
    task = sending_tasks.get(uid)
    if task:
        task.cancel()
        sending_tasks.pop(uid, None)
        return await message.answer("🛑 To‘xtatildi.", reply_markup=main_menu())
    await message.answer("❌ Jarayon yo‘q.")

# ================= MAIN =================
async def main():
    await client.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
