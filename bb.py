import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    ChatMemberUpdated
)
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# ================== O'ZGARTIRING ==================
API_TOKEN = "8365468834:AAFRszP8bFfWpQC7h6TX5_h5ZMzRO2uheV8"
CHANNEL_USERNAME = "@faqat_bzda"  # Kanal linki
BOT_USERNAME = "Hshahshskabot"
ADMIN_ID = 123456789  # @userinfobot orqali olingan ID
# ===================================================

bot = Bot(API_TOKEN)
dp = Dispatcher()

# User ma'lumotlar bazasi
users = {}

def get_user(uid):
    """Foydalanuvchi ma'lumotini olish / yaratish"""
    if uid not in users:
        users[uid] = {
            "balance": 0,
            "referrals": 0,
            "invited_by": None,
            "ref_rewarded": False,
            "penalty_applied": False
        }
    return users[uid]

def menu(is_admin=False):
    """Inline menyu yaratish (Aiogram 3.13 mos)"""
    kb = [
        [InlineKeyboardButton(text="📊 Balansim", callback_data="balance")],
        [InlineKeyboardButton(text="👥 Referallarim", callback_data="refs")],
        [InlineKeyboardButton(text="🔗 Referal linkim", callback_data="link")],
        [InlineKeyboardButton(text="📢 Kanal holati", callback_data="channel")],
        [InlineKeyboardButton(text="📜 Qoidalar", callback_data="rules")],
        [InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about")]
    ]
    if is_admin:
        kb.append([InlineKeyboardButton(text="🛠 Admin panel", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# =================== START COMMAND ===================
@dp.message(CommandStart())
async def start(msg: Message):
    uid = msg.from_user.id
    args = msg.text.split()
    user = get_user(uid)

    # Referal tekshirish
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if ref_id != uid:
                get_user(ref_id)  # Referalni bazaga qo'shish
                user["invited_by"] = ref_id
        except:
            pass

    await msg.answer(
        "👋 Xush kelibsiz!\n\n"
        "⭐ Yulduz faqat REFERAL orqali beriladi.\n"
        "⚠️ Kanalni tark etsangiz — jarima bo‘ladi.",
        reply_markup=menu(uid == ADMIN_ID)
    )

# =================== REAL-TIME CHANNEL EVENTS ===================
@dp.chat_member()
async def channel_events(event: ChatMemberUpdated):
    if event.chat.username != CHANNEL_USERNAME[1:]:
        return

    uid = event.from_user.id
    user = get_user(uid)
    inviter_id = user["invited_by"]

    # ➕ Kanalga kirish
    if event.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
        if inviter_id and not user["ref_rewarded"]:
            inviter = get_user(inviter_id)
            inviter["balance"] += 2.5
            inviter["referrals"] += 1
            user["ref_rewarded"] = True
            await bot.send_message(inviter_id, "🎉 Referalingiz kanalga a’zo bo‘ldi! ⭐ +2.5 yulduz")

    # ➖ Kanalni tark etish
    if event.new_chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        if inviter_id and user["ref_rewarded"] and not user["penalty_applied"]:
            inviter = get_user(inviter_id)
            inviter["balance"] -= 2.5
            user["penalty_applied"] = True
            await bot.send_message(inviter_id, "⚠️ Referalingiz kanaldan chiqdi. ❌ -2.5 ⭐ jarima")

# =================== CALLBACKS ===================
@dp.callback_query(F.data == "balance")
async def balance(call):
    u = get_user(call.from_user.id)
    await call.message.edit_text(
        f"📊 Balansingiz:\n\n⭐ {u['balance']}",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "refs")
async def refs(call):
    u = get_user(call.from_user.id)
    await call.message.edit_text(
        f"👥 Referallar soni: {u['referrals']}",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "link")
async def link(call):
    uid = call.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    await call.message.edit_text(
        f"🔗 Referal linkingiz:\n\n{link}\n\n"
        "Do‘stingiz kanalga kirsa → sizga ⭐",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "channel")
async def channel(call):
    await call.message.edit_text(
        f"📢 Kanal holati\n\n"
        f"🔗 Kanalga obuna bo‘lish: {CHANNEL_USERNAME}\n\n"
        "Referalingiz chiqib ketsa — jarima bo‘ladi.",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "rules")
async def rules(call):
    await call.message.edit_text(
        "📜 QOIDALAR:\n\n"
        "1️⃣ Yulduz faqat referal orqali\n"
        "2️⃣ Fake referal yo‘q\n"
        "3️⃣ Chiqib ketish — jarima\n"
        "4️⃣ Bir referal = 1 marta bonus",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "about")
async def about(call):
    await call.message.edit_text(
        "ℹ️ Professional referal bot\n"
        "🛡 Adolatli tizim\n"
        "⚙️ Real-time nazorat",
        reply_markup=menu(call.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "admin")
async def admin(call):
    if call.from_user.id != ADMIN_ID:
        return
    total_users = len(users)
    total_balance = sum(u["balance"] for u in users.values())
    await call.message.edit_text(
        f"🛠 ADMIN PANEL\n\n"
        f"👤 Users: {total_users}\n"
        f"⭐ Total stars: {total_balance}",
        reply_markup=menu(True)
    )

# =================== MAIN ===================
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())