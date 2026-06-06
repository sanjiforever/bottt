pkill -f bot.py
rm bot.py
cat > bot.py << 'MYEOF'
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date
import asyncio, json, os

BOT_TOKEN = "8871745549:AAGjU4ieXckOXNi3qzCsO64JAUMlmujiVLw"
ADMIN_ID = 8520739302
CONFIG_FILE = "config.json"
STATS_FILE = "stats.json"
USERS_FILE = "users.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "stars": 150,
        "stars_url": "https://t.me/tezstar_bot",
        "yordam": "sevaaaaaz",
        "rasm": "",
        "kanal_id": -1003986807955,
        "matn": "👋 Assalomu alaykum!\n\n🔒 Yopiq kanalga kirish uchun\n💫 atigi {stars} Stars tolag!\n\n⬇️ Tugmani bosing:"
    }

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"jami": 0, "bugun": 0, "sana": ""}

def save_stats(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

def add_user(user_id, username, full_name):
    users = load_users()
    users[str(user_id)] = {"username": username or "", "full_name": full_name}
    save_users(users)

def add_stat():
    stats = load_stats()
    bugun = str(date.today())
    if stats["sana"] != bugun:
        stats["bugun"] = 0
        stats["sana"] = bugun
    stats["jami"] += 1
    stats["bugun"] += 1
    save_stats(stats)

class AdminState(StatesGroup):
    waiting_stars = State()
    waiting_stars_url = State()
    waiting_yordam = State()
    waiting_rasm = State()
    waiting_kanal = State()
    waiting_matn = State()
    waiting_broadcast = State()
    waiting_user_id = State()
    waiting_user_msg = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    config = load_config()
    stars = config["stars"]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐ {stars} Stars tolab kirish", callback_data="tolov")],
        [InlineKeyboardButton(text="📲 Stars qanday olaman?", url=config["stars_url"])],
        [InlineKeyboardButton(text="📞 Yordam", url=f"https://t.me/{config['yordam']}")]
    ])
    matn = config.get("matn", "👋 Salom! {stars} Stars tolag!").replace("{stars}", str(stars))
    if config.get("rasm"):
        await message.answer_photo(photo=config["rasm"], caption=matn, reply_markup=keyboard)
    else:
        await message.answer(matn, reply_markup=keyboard)

@dp.message(F.text == "/admin")
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    stats = load_stats()
    users = load_users()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Stars narxini ozgartirish", callback_data="change_stars")],
        [InlineKeyboardButton(text="📲 Stars URL ozgartirish", callback_data="change_stars_url")],
        [InlineKeyboardButton(text="📞 Yordam linkini ozgartirish", callback_data="change_yordam")],
        [InlineKeyboardButton(text="🖼 Rasm qoyish", callback_data="change_rasm")],
        [InlineKeyboardButton(text="📢 Kanal ID ozgartirish", callback_data="change_kanal")],
        [InlineKeyboardButton(text="✏️ Bosh sahifa matnini ozgartirish", callback_data="change_matn")],
        [InlineKeyboardButton(text="📊 Sozlamalar", callback_data="settings")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="users_list")],
        [InlineKeyboardButton(text="📣 Hammaga xabar yuborish", callback_data="broadcast")],
        [InlineKeyboardButton(text="✉️ Bitta foydalanuvchiga xabar", callback_data="send_user")]
    ])
    await message.answer(
        f"👨‍💼 Admin panel\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"📈 Bugungi sotuvlar: {stats['bugun']}\n"
        f"📊 Jami sotuvlar: {stats['jami']}",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "change_matn")
async def change_matn(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer(
        "Yangi matnni kiriting!\n\n"
        "Stars sonini avtomatik korsatish uchun {stars} yozing\n\n"
        "Masalan:\n👋 Salom! {stars} Stars tolab kiring!"
    )
    await state.set_state(AdminState.waiting_matn)

@dp.message(AdminState.waiting_matn)
async def set_matn(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    config = load_config()
    config["matn"] = message.text
    save_config(config)
    await message.answer("✅ Matn ozgartirildi!")
    await state.clear()

@dp.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    config = load_config()
    await callback.message.answer(
        f"📊 Sozlamalar:\n\n"
        f"⭐ Stars: {config['stars']}\n"
        f"📲 Stars URL: {config['stars_url']}\n"
        f"📞 Yordam: @{config['yordam']}\n"
        f"📢 Kanal ID: {config['kanal_id']}\n"
        f"🖼 Rasm: {'Bor' if config.get('rasm') else 'Yoq'}\n"
        f"✏️ Matn: {config.get('matn', '')[:50]}..."
    )

@dp.callback_query(F.data == "users_list")
async def users_list(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    users = load_users()
    if not users:
        await callback.message.answer("Hali foydalanuvchi yoq!")
        return
    text = f"👥 Jami: {len(users)} ta\n\n"
    for uid, info in list(users.items())[:20]:
        username = f"@{info['username']}" if info['username'] else "username yoq"
        text += f"🆔 {uid} | {info['full_name']} | {username}\n"
    if len(users) > 20:
        text += f"\n...va yana {len(users)-20} ta"
    await callback.message.answer(text)

@dp.callback_query(F.data == "broadcast")
async def broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Hammaga yuboriladigan xabarni kiriting:")
    await state.set_state(AdminState.waiting_broadcast)

@dp.message(AdminState.waiting_broadcast)
async def send_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    ok = 0
    fail = 0
    for uid in users:
        try:
            await bot.send_message(int(uid), message.text)
            ok += 1
        except:
            fail += 1
    await message.answer(f"✅ Yuborildi: {ok}\n❌ Yuborilmadi: {fail}")
    await state.clear()

@dp.callback_query(F.data == "send_user")
async def send_user(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Foydalanuvchi ID sini kiriting:")
    await state.set_state(AdminState.waiting_user_id)

@dp.message(AdminState.waiting_user_id)
async def get_user_id(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(user_id=message.text)
    await message.answer("Xabarni kiriting:")
    await state.set_state(AdminState.waiting_user_msg)

@dp.message(AdminState.waiting_user_msg)
async def send_user_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    try:
        await bot.send_message(int(data["user_id"]), message.text)
        await message.answer("✅ Xabar yuborildi!")
    except:
        await message.answer("❌ Xabar yuborilmadi!")
    await state.clear()

@dp.callback_query(F.data == "change_stars")
async def change_stars(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Yangi Stars miqdorini kiriting:")
    await state.set_state(AdminState.waiting_stars)

@dp.message(AdminState.waiting_stars)
async def set_stars(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        stars = int(message.text)
        config = load_config()
        config["stars"] = stars
        save_config(config)
        await message.answer(f"✅ Stars {stars} ga ozgartirildi!")
        await state.clear()
    except:
        await message.answer("❌ Faqat raqam kiriting!")

@dp.callback_query(F.data == "change_stars_url")
async def change_stars_url(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Yangi Stars URL kiriting:")
    await state.set_state(AdminState.waiting_stars_url)

@dp.message(AdminState.waiting_stars_url)
async def set_stars_url(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    config = load_config()
    config["stars_url"] = message.text
    save_config(config)
    await message.answer("✅ Stars URL ozgartirildi!")
    await state.clear()

@dp.callback_query(F.data == "change_yordam")
async def change_yordam(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Yangi yordam username kiriting:")
    await state.set_state(AdminState.waiting_yordam)

@dp.message(AdminState.waiting_yordam)
async def set_yordam(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    config = load_config()
    config["yordam"] = message.text.replace("@", "")
    save_config(config)
    await message.answer("✅ Yordam ozgartirildi!")
    await state.clear()

@dp.callback_query(F.data == "change_rasm")
async def change_rasm(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Rasmni yuboring:")
    await state.set_state(AdminState.waiting_rasm)

@dp.message(AdminState.waiting_rasm, F.photo)
async def set_rasm(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    config = load_config()
    config["rasm"] = message.photo[-1].file_id
    save_config(config)
    await message.answer("✅ Rasm saqlandi!")
    await state.clear()

@dp.callback_query(F.data == "change_kanal")
async def change_kanal(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Yangi kanal ID kiriting:")
    await state.set_state(AdminState.waiting_kanal)

@dp.message(AdminState.waiting_kanal)
async def set_kanal(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        kanal_id = int(message.text)
        config = load_config()
        config["kanal_id"] = kanal_id
        save_config(config)
        await message.answer(f"✅ Kanal ID ozgartirildi: {kanal_id}")
        await state.clear()
    except:
        await message.answer("❌ Togri ID kiriting!")

@dp.callback_query(F.data == "tolov")
async def tolov(callback: types.CallbackQuery):
    config = load_config()
    stars = config["stars"]
    await bot.send_invoice(
        callback.message.chat.id,
        title="Kanal obunasi",
        description=f"{stars} Stars tolab kanalga kiring!",
        payload="sub",
        currency="XTR",
        prices=[LabeledPrice(label="Obuna", amount=stars)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def paid(message: types.Message):
    config = load_config()
    add_stat()
    link = await bot.create_chat_invite_link(config["kanal_id"], member_limit=1)
    await message.answer(f"✅ Tolov qabul qilindi!\n\n🔗 1 martali havola:\n{link.invite_link}\n\n⚠️ Havolani saqlang!")

async def main():
    print("Bot ishlamoqda...")
    await dp.start_polling(bot)

asyncio.run(main())
MYEOF
