import asyncio
import logging
from datetime import datetime, timedelta

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



logging.basicConfig(level=logging.INFO)

# ================== SOZLAMALAR ==================
TOKEN = "8285781260:AAE3Oq6ZyCrPHeaSvMJjZiV7Q3xChHEMlVc"
ADMIN_ID = 6302873072  # admin Telegram ID
GROUP_IDS = [-5094653291, -5094653291, -5078793194, -1002589715287]  # Guruhlar ID'lari
# =================================================

# Bot va Dispatcher
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

approved_users = set()
sending_tasks = {}

# ================== KLAVIATURALAR ==================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📢 E’lon yuborish"))
    return kb

def back_button():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("◀️ Orqaga"))

def interval_buttons():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 daqiqa", callback_data="interval_5")],
        [InlineKeyboardButton(text="7 daqiqa", callback_data="interval_7")],
        [InlineKeyboardButton(text="10 daqiqa", callback_data="interval_10")],
        [InlineKeyboardButton(text="15 daqiqa", callback_data="interval_15")]
    ])
    return kb

# ================== START ==================
@dp.message(CommandStart())
async def start_cmd(message: Message):
    user_id = message.from_user.id
    if user_id in approved_users:
        await message.answer("👋 Xush kelibsiz! Quyidagi menyudan foydalaning:", reply_markup=main_menu())
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📨 So‘rovnoma yuborish", callback_data=f"request_access_{user_id}")]
        ])
        await message.answer(
            "🛑 Botni ishlatish uchun adminga so‘rovnoma yuboring.",
            reply_markup=markup
        )

# ================== ADMIN SO‘ROV ==================
@dp.callback_query(F.data.startswith("request_access_"))
async def request_access(call: CallbackQuery):
    user_id = int(call.data.split("_")[-1])
    user = call.from_user
    text = f"👤 <b>{user.full_name}</b> (ID: <code>{user_id}</code>) botga qo‘shilmoqchi."

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"deny_{user_id}")
        ]
    ])
    await bot.send_message(ADMIN_ID, text, reply_markup=markup)
    await call.message.edit_text("📨 So‘rovnoma adminga yuborildi. Javobni kuting.")

# ================== ADMIN JAVOBI ==================
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(call: CallbackQuery):
    user_id = int(call.data.split("_")[-1])
    approved_users.add(user_id)
    await bot.send_message(user_id, "✅ Sizga botdan foydalanish uchun ruxsat berildi!", reply_markup=main_menu())
    await call.message.edit_text(f"✅ {user_id} foydalanuvchiga ruxsat berildi.")

@dp.callback_query(F.data.startswith("deny_"))
async def deny_user(call: CallbackQuery):
    user_id = int(call.data.split("_")[-1])
    await bot.send_message(user_id, "❌ Sizning so‘rovingiz rad etildi.")
    await call.message.edit_text(f"❌ {user_id} foydalanuvchiga ruxsat berilmadi.")

# ================== E’LON YARATISH ==================
@dp.message(F.text == "📢 E’lon yuborish")
async def elon_start(message: Message):
    if message.from_user.id not in approved_users:
        await message.answer("🛑 Sizda hali ruxsat yo‘q.")
        return
    await message.answer("✍️ E’lon matnini kiriting:", reply_markup=back_button())
    await storage.set_state(message.from_user.id, "elon_text")

@dp.message(F.text == "◀️ Orqaga")
async def go_back(message: Message):
    await storage.set_state(message.from_user.id, None)
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())

@dp.message(F.text, lambda msg, state=None: storage.get_state(msg.from_user.id) == "elon_text")
async def get_text(message: Message):
    await storage.update_data(message.from_user.id, {"text": message.text})
    await storage.set_state(message.from_user.id, "elon_photo")
    await message.answer("🖼 Rasm yuboring (majburiy):")

@dp.message(F.photo, lambda msg, state=None: storage.get_state(msg.from_user.id) == "elon_photo")
async def get_photo(message: Message):
    photo_id = message.photo[-1].file_id
    user_data = await storage.get_data(message.from_user.id)
    user_data["photo"] = photo_id
    await storage.update_data(message.from_user.id, user_data)

    await storage.set_state(message.from_user.id, "interval")
    await message.answer("⏱ Xabar yuborish oraliq vaqtini tanlang:", reply_markup=interval_buttons())

# ================== INTERVAL TANLASH ==================
@dp.callback_query(F.data.startswith("interval_"))
async def choose_interval(call: CallbackQuery):
    interval = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    user_data = await storage.get_data(user_id)

    text = user_data["text"]
    photo = user_data["photo"]

    await call.message.edit_text(f"✅ Xabar yuborish boshlandi ({interval} daqiqa oraliqda).")

    stop_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🛑 To‘xtatish"))
    await bot.send_message(user_id, "📨 E’lon yuborish boshlandi.", reply_markup=stop_markup)

    task = asyncio.create_task(send_periodically(user_id, text, photo, interval))
    sending_tasks[user_id] = task

# ================== XABAR YUBORISH FUNKSIYASI ==================
async def send_periodically(user_id, text, photo, interval):
    end_time = datetime.now() + timedelta(hours=24)
    while datetime.now() < end_time:
        for group_id in GROUP_IDS:
            try:
                await bot.send_photo(chat_id=group_id, photo=photo, caption=text)
                await bot.send_message(user_id, f"✅ Yuborildi: {group_id}")
            except Exception as e:
                await bot.send_message(user_id, f"⚠️ Yuborilmadi: {group_id}\n{e}")
        await asyncio.sleep(interval * 60)
    await bot.send_message(user_id, "⏰ 24 soat tugadi. Yuborish avtomatik to‘xtadi.", reply_markup=main_menu())
    sending_tasks.pop(user_id, None)

# ================== TO‘XTATISH ==================
@dp.message(F.text == "🛑 To‘xtatish")
async def stop_sending(message: Message):
    user_id = message.from_user.id
    task = sending_tasks.get(user_id)
    if task:
        task.cancel()
        sending_tasks.pop(user_id, None)
        await message.answer("🛑 Yuborish to‘xtatildi.", reply_markup=main_menu())
    else:
        await message.answer("❌ Hech qanday yuborish jarayoni topilmadi.", reply_markup=main_menu())

# ================== RUN ==================
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
