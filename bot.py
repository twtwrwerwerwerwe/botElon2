# bot.py
# -*- coding: utf-8 -*-
import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

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
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== SOZLAMALAR (Siz bergan token, admin va guruhlar) ==================
TOKEN = "8285781260:AAE3Oq6ZyCrPHeaSvMJjZiV7Q3xChHEMlVc"
ADMIN_ID = 6302873072

GROUP_IDS = [
    -2170948358, -2493445581, -1778953138, -1731045491, -2120516658, -2484755801,
    -2026648371, -2234686912, -1694580843, -1746287379, -2178115911, -1776683876,
    -1415509604, -2237661481, -1915102512, -1444845133, -1811533352, -1647088954,
    -2005244602, -2111866462, -1241848114, -2241634256, -1289452204, -1667139052,
    -2039052299, -1850189100, -2115024618, -2235474099, -1742400002, -1658823031,
    -2191184691, -1822984931, -2414599348, -2312848611, -2267157287, -2781319220,
    -2378309722, -1941704640, -1603962138, -1997802565, -1817667341, -1512582033,
    -2007946366, -2446537677, -1683254773, -1927229818, -1185367329, -2167599554,
    -2157073492, -1475892315, -1648210608, -1794714906, -2678507364, -1616839980,
    -2440006604, -2038219005, -1492373877, -1810620276, -2272987933, -2335367289,
    -2217965858, -2113519793, -1641418825, -2453451103, -2423815896, -1450758678,
    -2617176671, -2620354767, -2257001893, -1879991848, -1695104164, -1621229157,
    -1432288141, -2041700993, -1499767213, -1698139271, -1626903329, -2259099483,
    -2108506175, -1970736982, -2126029787, -2389269227, -2024422960, -1874884337,
    -2379670381, -1726402253, -2589715287, -2312784860, -5003347692, -1923757739,
    -1948039973
]
# ======================================================================================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ================== FILES ==================
APPROVED_FILE = "approved.json"
ELONS_FILE = "elons.json"  # stores active and queued elons

# ================== IN-MEMORY STRUCTURES ==================
approved_users: Dict[str, str] = {}   # user_id_str -> display_name
pending_requests: Dict[str, str] = {}  # user_id_str -> display_name
sending_tasks: Dict[int, asyncio.Task] = {}  # user_id_int -> asyncio.Task

# ================== UTIL: load/save approved ==================
def load_json_file(path: str) -> Any:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.exception(f"{path} yuklashda xatolik")
        return {}

def save_json_file(path: str, data: Any):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception(f"{path} saqlashda xatolik")

def load_approved():
    global approved_users
    data = load_json_file(APPROVED_FILE)
    if isinstance(data, dict):
        approved_users = data
    else:
        approved_users = {}
    logger.info(f"Approved loaded: {len(approved_users)} users")

def save_approved():
    save_json_file(APPROVED_FILE, approved_users)
    logger.info("approved.json saqlandi")

# ================== ELONS (e'lonlar) ==================
# Structure of elons.json:
# {
#    "<elon_id>": {
#        "user_id": <int>,
#        "display_name": "<str>",
#        "text": "<str>",
#        "photo": "<file_id>",
#        "interval": <minutes>,
#        "start_time": "<ISO datetime str>"
#    },
#    ...
# }
def load_elons() -> Dict[str, Dict]:
    data = load_json_file(ELONS_FILE)
    if isinstance(data, dict):
        return data
    return {}

def save_elons(elons: Dict[str, Dict]):
    save_json_file(ELONS_FILE, elons)
    logger.info("elons.json saqlandi")

# load on start
load_approved()
elons = load_elons()  # in-memory copy of elons.json

# ================== FSM STATES ==================
class RequestStates(StatesGroup):
    waiting_name = State()

class ElonStates(StatesGroup):
    text = State()
    photo = State()
    interval = State()

# ================== KEYBOARDS ==================
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

def admin_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Odamla")],
            [KeyboardButton(text="📊 Statistik"), KeyboardButton(text="🔄 Qayta yuklash")],
        ],
        resize_keyboard=True
    )

def interval_buttons():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="5 daqiqa", callback_data="interval_5")],
            [InlineKeyboardButton(text="7 daqiqa", callback_data="interval_7")],
            [InlineKeyboardButton(text="10 daqiqa", callback_data="interval_10")],
            [InlineKeyboardButton(text="15 daqiqa", callback_data="interval_15")],
        ]
    )
    return kb

# ================== START ==================
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id in approved_users:
        await message.answer("👋 Xush kelibsiz! Quyidagi menyudan foydalaning:", reply_markup=main_menu())
    else:
        await state.set_state(RequestStates.waiting_name)
        await message.answer(
            "🛑 Botni ishlatish uchun ruxsat kerak.\nIltimos, ismingizni yozib yuboring (u butun ismingiz yoki siz tanlagan nom bo‘lsin).",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📨 So‘rovnoma yuborish")]], resize_keyboard=True)
        )

# ================== REQUEST: user sends name ==================
@dp.message(RequestStates.waiting_name)
async def receive_name(message: Message, state: FSMContext):
    name = message.text.strip()
    user_id = str(message.from_user.id)
    if not name or len(name) > 64:
        await message.answer("Iltimos, qisqa va aniq ism kiriting (1-64 belgi).")
        return

    pending_requests[user_id] = name

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"deny_{user_id}")
            ]
        ]
    )
    requester = message.from_user
    text = f"👤 <b>{requester.full_name}</b>\n📛 Nom: <i>{name}</i>\nID: <code>{user_id}</code>\nfoydalanuvchi botga qo‘shilmoqchi."
    try:
        await bot.send_message(ADMIN_ID, text, reply_markup=markup)
        await message.answer("📨 So‘rovnoma yuborildi. Javobni kuting.", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Orqaga")]], resize_keyboard=True))
    except Exception:
        logger.exception("adminga so'rov yuborishda xato:")
        await message.answer("❗ So‘rov yuborilmadi (admin bilan bog‘lanish muammosi). Iltimos, keyinroq urinib ko‘ring.")
    finally:
        await state.clear()

# ================== ADMIN: approve/deny callbacks ==================
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo‘q.", show_alert=True)
        return

    user_id = call.data.split("_", 1)[1]
    name = pending_requests.get(user_id, None)
    if not name:
        name = approved_users.get(user_id)
        if not name:
            await call.message.edit_text("❗ Bu so‘rov topilmadi yoki allaqachon qayta ishlangan.")
            return

    approved_users[user_id] = name
    save_approved()
    pending_requests.pop(user_id, None)

    try:
        await bot.send_message(int(user_id), "✅ Sizga botdan foydalanish uchun ruxsat berildi!", reply_markup=main_menu())
    except Exception:
        logger.exception("Foydalanuvchiga ruxsat haqida habar yuborishda xato")

    await call.message.edit_text(f"✅ {name} (ID: {user_id}) ga ruxsat berildi.")

@dp.callback_query(F.data.startswith("deny_"))
async def deny_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo‘q.", show_alert=True)
        return
    user_id = call.data.split("_", 1)[1]
    name = pending_requests.pop(user_id, None)
    try:
        await bot.send_message(int(user_id), "❌ Sizning so‘rovingiz rad etildi.")
    except Exception:
        logger.exception("deny - userga habar yuborishda xato")
    await call.message.edit_text(f"❌ {name or user_id} ning so‘rovi rad etildi.")

# ================== ADMIN: "Odamla" - ro'yxat ko'rsatish ==================
@dp.message(F.text == "👥 Odamla")
async def show_people(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu funksiyaga faqat admin ega.")
        return

    if not approved_users:
        await message.answer("👥 Hozircha tasdiqlangan odamlar yo‘q.", reply_markup=admin_main_menu())
        return

    buttons = []
    for uid_str, display_name in approved_users.items():
        buttons.append([InlineKeyboardButton(text=display_name, callback_data=f"manage_{uid_str}")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("👥 Tasdiqlangan foydalanuvchilar:", reply_markup=kb)

@dp.callback_query(F.data.startswith("manage_"))
async def manage_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo‘q.", show_alert=True)
        return

    uid_str = call.data.split("_", 1)[1]
    name = approved_users.get(uid_str)
    if not name:
        await call.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Chiqarib tashlash", callback_data=f"remove_{uid_str}")],
        [InlineKeyboardButton(text="✅ Qoldirish", callback_data=f"keep_{uid_str}")],
    ])
    await call.message.edit_text(f"👤 <b>{name}</b>\nID: <code>{uid_str}</code>\nNimani qilmoqchisiz?", reply_markup=kb)

@dp.callback_query(F.data.startswith("keep_"))
async def keep_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo‘q.", show_alert=True)
        return
    uid_str = call.data.split("_", 1)[1]
    name = approved_users.get(uid_str)
    await call.message.edit_text(f"✅ {name} (ID: {uid_str}) qoldirildi.", reply_markup=admin_main_menu())

@dp.callback_query(F.data.startswith("remove_"))
async def remove_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo‘q.", show_alert=True)
        return
    uid_str = call.data.split("_", 1)[1]
    name = approved_users.pop(uid_str, None)
    save_approved()
    # cancel any sending task if exists
    try:
        uid_int = int(uid_str)
        task = sending_tasks.get(uid_int)
        if task:
            task.cancel()
            sending_tasks.pop(uid_int, None)
    except Exception:
        pass

    if name:
        try:
            await bot.send_message(int(uid_str), "❗ Siz botdan chiqarib tashlandingiz. Endi e'lon yuborolmaysiz.")
        except Exception:
            logger.exception("removed userga habar yuborishda xato")

    await call.message.edit_text(f"❌ {name or uid_str} botdan chiqarildi.", reply_markup=admin_main_menu())

# ================== ADMIN: statistik va reload (oddiy) ==================
@dp.message(F.text == "📊 Statistik")
async def statistik(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu funksiyaga faqat admin ega.")
        return
    count = len(approved_users)
    await message.answer(f"📊 Tasdiqlangan foydalanuvchilar soni: {count}", reply_markup=admin_main_menu())

@dp.message(F.text == "🔄 Qayta yuklash")
async def reload_data(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu funksiyaga faqat admin ega.")
        return
    load_approved()
    # reload elons from disk and restart tasks for non-expired ones
    global elons
    elons = load_elons()
    await message.answer("🔄 Ma'lumotlar qayta yuklandi.", reply_markup=admin_main_menu())
    # restart senders for loaded elons
    asyncio.create_task(resume_elons_on_startup())

# ================== E’LON YARATISH ==================
@dp.message(F.text == "📢 E’lon yuborish")
async def elon_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id not in approved_users:
        await message.answer("🛑 Sizda hali ruxsat yo‘q.")
        return
    await state.set_state(ElonStates.text)
    await message.answer("✍️ E’lon matnini kiriting:", reply_markup=back_button())

@dp.message(F.text == "◀️ Orqaga")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("🏠 Admin menyu:", reply_markup=admin_main_menu())
    else:
        await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())

@dp.message(ElonStates.text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(ElonStates.photo)
    await message.answer("🖼 Iltimos rasm yuboring (majburiy):")

@dp.message(ElonStates.photo)
async def get_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❗ Rasm yuboring iltimos.")
        return
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(ElonStates.interval)
    await message.answer("⏱ Xabar yuborish oraliq vaqtini tanlang:", reply_markup=interval_buttons())

@dp.callback_query(F.data.startswith("interval_"))
async def choose_interval(call: CallbackQuery, state: FSMContext):
    interval = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    data = await state.get_data()
    text = data.get("text")
    photo = data.get("photo")
    if not text or not photo:
        await call.message.edit_text("❗ E'lon ma'lumotlari toʻliq emas. Iltimos boshidan yuboring.")
        await state.clear()
        return

    # Save elon to elons.json with timestamp
    elon_id = f"{user_id}_{int(datetime.now().timestamp())}"
    elon_obj = {
        "user_id": user_id,
        "display_name": approved_users.get(str(user_id), ""),
        "text": text,
        "photo": photo,
        "interval": interval,
        "start_time": datetime.now().isoformat()
    }
    elons[elon_id] = elon_obj
    save_elons(elons)

    await call.message.edit_text(f"✅ Xabar yuborish boshlandi ({interval} daqiqa oraliqda).")

    stop_markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛑 To‘xtatish")]],
        resize_keyboard=True
    )
    await bot.send_message(user_id, "📨 E’lon yuborish boshlandi. To‘xtatish uchun tugmani bosing.", reply_markup=stop_markup)

    task = asyncio.create_task(send_periodically(int(user_id), elon_id))
    sending_tasks[int(user_id)] = task
    await state.clear()

# ================== XABAR YUBORISH FUNKSIYASI ==================
async def send_periodically(user_id_int: int, elon_id: str):
    """
    Sends the elon (photo + caption) to all GROUP_IDS periodically based on elon.interval.
    Stops automatically after 24 hours from elon.start_time, or when task is cancelled.
    """
    try:
        elon = elons.get(elon_id)
        if not elon:
            logger.warning("Elon topilmadi: %s", elon_id)
            return

        start_time = datetime.fromisoformat(elon["start_time"])
        end_time = start_time + timedelta(hours=24)
        interval_minutes = int(elon.get("interval", 5))
        text = elon.get("text", "")
        photo = elon.get("photo")

        while datetime.now() < end_time:
            for group_id in GROUP_IDS:
                try:
                    await bot.send_photo(chat_id=group_id, photo=photo, caption=text)
                    # notify sender about success for each group
                    try:
                        await bot.send_message(user_id_int, f"✅ Yuborildi: {group_id}")
                    except Exception:
                        logger.debug("Senderga yuborildi xabari yuborilmadi")
                except Exception as e:
                    # if fails (bot not in group or permission), notify sender
                    try:
                        await bot.send_message(user_id_int, f"⚠️ Yuborilmadi: {group_id}\n{e}")
                    except Exception:
                        logger.debug("Senderga yuborilmadi - error haqida xabar jo'natilmadi")
            # sleep for interval minutes
            await asyncio.sleep(interval_minutes * 60)
        # after 24 hours, remove elon and inform user
        try:
            await bot.send_message(user_id_int, "⏰ 24 soat tugadi. Yuborish avtomatik to‘xtadi.", reply_markup=main_menu())
        except Exception:
            pass
    except asyncio.CancelledError:
        # task cancelled by user or cleaner
        try:
            await bot.send_message(user_id_int, "🛑 Yuborish to‘xtatildi (foydalanuvchi yoki admin tomonidan).", reply_markup=main_menu())
        except Exception:
            pass
        raise
    except Exception:
        logger.exception("send_periodically ishlashida xato")
    finally:
        # cleanup: remove elon from storage if exists and save
        if elon_id in elons:
            elons.pop(elon_id, None)
            save_elons(elons)
        sending_tasks.pop(user_id_int, None)

# ================== TO‘XTATISH ==================
@dp.message(F.text == "🛑 To‘xtatish")
async def stop_sending(message: Message):
    user_id = message.from_user.id
    task = sending_tasks.get(user_id)
    # find elon(s) by this user
    user_elon_ids = [eid for eid, e in elons.items() if int(e.get("user_id")) == user_id]
    if task:
        task.cancel()
        sending_tasks.pop(user_id, None)
        # remove associated elons
        for eid in user_elon_ids:
            elons.pop(eid, None)
        save_elons(elons)
        await message.answer("🛑 Yuborish to‘xtatildi.", reply_markup=main_menu())
    else:
        # If no running task but elons exist (maybe scheduled by previous run), remove them
        if user_elon_ids:
            for eid in user_elon_ids:
                elons.pop(eid, None)
            save_elons(elons)
            await message.answer("🛑 E'lon(lar) bekor qilindi.", reply_markup=main_menu())
        else:
            await message.answer("❌ Hech qanday yuborish jarayoni topilmadi.", reply_markup=main_menu())

# ================== ADMIN QUICK START MENU (agar admin /start qilsa) ==================
@dp.message()
async def catch_all(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🏠 Admin menyu:", reply_markup=admin_main_menu())
    else:
        uid = str(message.from_user.id)
        if uid in approved_users:
            await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu())
        else:
            await message.answer("Bot yordamiga xush kelibsiz. /start ni bosing va so‘rov yuboring.")

# ================== ELON CLEANER (background) ==================
async def elon_cleaner_loop():
    """
    Periodically (every 5 minutes) check elons and remove those older than 24 hours.
    Cancel associated sending tasks if running.
    """
    while True:
        try:
            now = datetime.now()
            removed = []
            for eid, e in list(elons.items()):
                try:
                    start = datetime.fromisoformat(e["start_time"])
                except Exception:
                    # if malformed, remove it
                    start = now - timedelta(days=2)
                if now >= start + timedelta(hours=24):
                    # cancel task if running for this user
                    try:
                        uid = int(e["user_id"])
                        task = sending_tasks.get(uid)
                        if task:
                            task.cancel()
                            sending_tasks.pop(uid, None)
                    except Exception:
                        pass
                    removed.append(eid)
            if removed:
                for eid in removed:
                    elons.pop(eid, None)
                save_elons(elons)
                logger.info("Elon cleaner removed %d expired elon(s).", len(removed))
        except Exception:
            logger.exception("Elon cleaner ishlashida xato")
        await asyncio.sleep(300)  # 5 daqiqa

# ================== RESUME ELONS ON STARTUP ==================
async def resume_elons_on_startup():
    """
    Called after bot starts: restart send_periodically for any saved elons that are still within 24h.
    """
    global elons
    now = datetime.now()
    started = 0
    for eid, e in list(elons.items()):
        try:
            start = datetime.fromisoformat(e["start_time"])
        except Exception:
            # malformed => drop
            elons.pop(eid, None)
            continue
        if now < start + timedelta(hours=24):
            uid = int(e["user_id"])
            if uid not in sending_tasks:
                task = asyncio.create_task(send_periodically(uid, eid))
                sending_tasks[uid] = task
                started += 1
        else:
            # expired, remove
            elons.pop(eid, None)
    if started:
        logger.info("Resume: %d elon task qayta ishga tushirildi.", started)
    save_elons(elons)

# ================== RUN ==================
async def main():
    # resume elons and start cleaner
    await resume_elons_on_startup()
    asyncio.create_task(elon_cleaner_loop())
    logger.info("Bot ishga tushmoqda... polling boshlandi.")
    try:
        await dp.start_polling(bot)
    finally:
        # saqlab qo'yamiz exitda ham
        save_approved()
        save_elons(elons)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtadi.")
