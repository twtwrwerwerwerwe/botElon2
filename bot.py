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

# Telethon
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserAlreadyParticipantError, ChannelPrivateError, InviteHashInvalidError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = "8285781260:AAE3Oq6ZyCrPHeaSvMJjZiV7Q3xChHEMlVc"   # put your bot token
ADMIN_ID = 6302873072

API_ID = 32460736
API_HASH = "285e2a8556652e6f4ffdb83658081031"
SESSION_NAME = "session"  # telethon session file name (session.session)

# Put your targets here (mix of int IDs and t.me links)

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

# ================= AIROGRAM INIT =================
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# TELETHON CLIENT
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

sending_tasks = {}
approved_users = set()

# ================= HELPERS =================
def extract_tme_path(link: str) -> str:
    """
    Normalize t.me links to the path component.
    Examples:
      https://t.me/username -> username
      t.me/username -> username
      https://t.me/+invitehash -> +invitehash
    """
    if not isinstance(link, str):
        return link
    link = link.strip()
    # Remove protocol
    if link.startswith("https://"):
        link = link[len("https://"):]
    if link.startswith("http://"):
        link = link[len("http://"):]
    # Remove possible leading 't.me/'
    if link.startswith("t.me/"):
        link = link[len("t.me/"):]
    # Remove trailing slashes
    return link.rstrip("/")


async def safe_join(target: Any) -> str:
    """
    Attempts to join a channel/group.
    Accepts:
      - int (ID)
      - username string (e.g. "username" or "https://t.me/username")
      - private invite string like "+abcdefg" or "https://t.me/+abcdefg"
    Returns status string for logging.
    """
    try:
        # If it's an integer id -> get entity then join
        if isinstance(target, int):
            try:
                entity = await client.get_entity(target)
            except Exception as e:
                return f"get_entity_error({e})"
            try:
                await client(JoinChannelRequest(entity))
                return "joined"
            except UserAlreadyParticipantError:
                return "already"
            except FloodWaitError as fw:
                logger.warning("FloodWait %s seconds for target %s", fw.seconds, target)
                await asyncio.sleep(fw.seconds + 1)
                return await safe_join(target)
            except Exception as e:
                return f"join_error({e})"

        # If it's a string (link or username)
        if isinstance(target, str):
            path = extract_tme_path(target)

            # Private invite (starts with +)
            if path.startswith("+"):
                invite_hash = path[1:]
                try:
                    await client(ImportChatInviteRequest(invite_hash))
                    return "joined_private"
                except InviteHashInvalidError:
                    return "invalid_invite_hash"
                except UserAlreadyParticipantError:
                    return "already"
                except FloodWaitError as fw:
                    logger.warning("FloodWait %s seconds for invite %s", fw.seconds, target)
                    await asyncio.sleep(fw.seconds + 1)
                    return await safe_join(target)
                except ChannelPrivateError:
                    return "channel_private_error"
                except Exception as e:
                    return f"import_error({e})"

            # Public username / channel
            try:
                # Try join by username/path directly
                await client(JoinChannelRequest(path))
                return "joined"
            except UserAlreadyParticipantError:
                return "already"
            except FloodWaitError as fw:
                logger.warning("FloodWait %s seconds for target %s", fw.seconds, target)
                await asyncio.sleep(fw.seconds + 1)
                return await safe_join(target)
            except Exception as e:
                # Sometimes JoinChannelRequest with string fails; fallback: resolve entity then join by entity
                try:
                    entity = await client.get_entity(path)
                    try:
                        await client(JoinChannelRequest(entity))
                        return "joined"
                    except UserAlreadyParticipantError:
                        return "already"
                    except FloodWaitError as fw2:
                        logger.warning("FloodWait %s seconds for entity %s", fw2.seconds, target)
                        await asyncio.sleep(fw2.seconds + 1)
                        return await safe_join(target)
                    except Exception as e2:
                        return f"join_entity_error({e2})"
                except Exception as e3:
                    return f"resolve_error({e3})"

    except Exception as e:
        return f"unknown_error({e})"


async def auto_join_all():
    """
    Iterate over TARGETS and try to join each one safely.
    Prints progress to console.
    """
    print("=== AUTO JOIN BOSHLANDI ===")
    await client.start()
    join_count = 0
    failed = []

    for target in TARGETS:
        print(f"➡️ Qo‘shilmoqda: {target}")
        try:
            status = await safe_join(target)
            if status in ("joined", "joined_private"):
                print(f"✅ Qo‘shildi → {target}")
            elif status == "already":
                print(f"➡️ Allaqachon qo‘shilgan → {target}")
            else:
                print(f"⚠️ Xato → {target}: {status}")
                failed.append((target, status))
        except Exception as e:
            print(f"⚠️ Kutilmagan xato → {target}: {e}")
            failed.append((target, str(e)))

        join_count += 1

        # Anti-flood strategy
        # Small random sleep between joins
        sleep_sec = random.randint(5, 12)
        await asyncio.sleep(sleep_sec)

        # After each 20 joins, bigger pause
        if join_count % 20 == 0:
            print("--- 20 ta qo‘shildi, 30 sekund pauza ---")
            await asyncio.sleep(30)

    print("=== AUTO JOIN TUGADI ===")
    if failed:
        print("Quyidagi join bo‘lmaganlar ro‘yxati:")
        for t, s in failed:
            print(f" - {t}  => {s}")
    print("Bot FULL WORK MODE ga o‘tdi!")

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

def interval_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="5 daqiqa", callback_data="interval_5")],
            [InlineKeyboardButton(text="7 daqiqa", callback_data="interval_7")],
            [InlineKeyboardButton(text="10 daqiqa", callback_data="interval_10")],
            [InlineKeyboardButton(text="15 daqiqa", callback_data="interval_15")],
        ]
    )

# ================= START / ADMIN LOGIC ==================
@dp.message(CommandStart())
async def start_cmd(message: Message):
    uid = message.from_user.id
    if uid in approved_users:
        return await message.answer("👋 Xush kelibsiz!", reply_markup=main_menu())

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📨 So‘rov yuborish", callback_data=f"request_{uid}")]
        ]
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

    await bot.send_message(ADMIN_ID, f"👤 <b>{u.full_name}</b>\nID: <code>{user_id}</code>", reply_markup=markup)
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

# ================ E’LON BOSHLASH =================
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

# =============== INTERVAL TANLASH =================
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

# ============ TELETHON SEND ==============
async def send_loop(uid: int, text: str, photo_file_id: str, interval: int):
    await client.start()
    # download photo via aiogram to a local file
    local_dir = "temp_media"
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, f"{photo_file_id.replace('/', '_')}.jpg")
    await bot.download(photo_file_id, local_path)

    end = datetime.now() + timedelta(hours=24)
    while datetime.now() < end:
        for target in TARGETS:
            try:
                # resolve entity (works for id, username, link)
                # if target is int, get_entity will handle it
                entity = None
                try:
                    if isinstance(target, int):
                        entity = await client.get_entity(target)
                    else:
                        # for link-like strings, try extract path and get_entity
                        path = extract_tme_path(target)
                        # for private invites (starts with '+') we can't get entity here; skip send
                        if path.startswith("+"):
                            await bot.send_message(uid, f"⚠️ Private invite (skip send): {target}")
                            continue
                        entity = await client.get_entity(path)
                except Exception as e:
                    await bot.send_message(uid, f"⚠️ Entity resolve failed for {target}: {e}")
                    continue

                await client.send_file(entity, local_path, caption=text)
                await bot.send_message(uid, f"✅ Yuborildi: {target}")
                # small delay between sends to avoid flood
                await asyncio.sleep(random.uniform(1.0, 2.5))
            except FloodWaitError as fw:
                await bot.send_message(uid, f"⏳ FloodWait {fw.seconds}s for {target}. Waiting...")
                await asyncio.sleep(fw.seconds + 1)
            except Exception as e:
                await bot.send_message(uid, f"⚠️ Xato yuborishda: {target}\n{e}")

        await asyncio.sleep(interval * 60)

    # cleanup
    try:
        if os.path.exists(local_path):
            os.remove(local_path)
    except Exception:
        pass

    await bot.send_message(uid, "⏰ 24 soat tugadi.", reply_markup=main_menu())
    sending_tasks.pop(uid, None)

# ============ STOP =================
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
    # Start telethon client then auto-join all targets
    await client.start()
    # run auto join (safe)
    try:
        await auto_join_all()
    except Exception as e:
        logger.exception("Auto-join davomida xato: %s", e)

    # Start aiogram polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
