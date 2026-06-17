import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.context import FSMContext

from states import RegisterState, BroadcastState
from database import (
    add_user,
    get_users,
    get_all_users,
    users_count
)

TOKEN = "8805499299:AAGXx6apgd7Ed02nN4HLSjml0PUeYg1Yqo4"
ADMIN_ID = 8385570192

bot = Bot(token=TOKEN)
dp = Dispatcher()

mahallalar = [
    "Al-Xorazmiy","Andijon","Birdamlik","Bobur","Bogʻishamol",
    "Buloqariq","Bunyodkor","Doʻstlik","Farxod","Fargʻona",
    "Hamid Olimjon","Jomiy","Madaniyat","Maʼrifat","Metallurg",
    "Muqimiy","Mustaqillik","Navroʻz","Nurli yoʻl",
    "Obod turmush","Oʻzbekiston","Paxtakor",
    "Qosim ota Farmonov","Samarqand","Sayhun",
    "Sementchi","Sirdaryo","Shirin","Taraqqiyot",
    "Tinchlik","Turkiston","Yangi hayot","Yoshlik"
]

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Telefon raqam yuborish",
                request_contact=True
            )
        ]
    ],
    resize_keyboard=True
)

mahalla_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=m)] for m in mahallalar],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Foydalanuvchilar soni")],
        [KeyboardButton(text="📋 Ishtirokchilar")],
        [KeyboardButton(text="📢 Xabar yuborish")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Admin panelga xush kelibsiz",
            reply_markup=admin_kb
        )
        return

    await state.clear()
    await message.answer("Ismingizni kiriting:")
    await state.set_state(RegisterState.first_name)


@dp.message(RegisterState.first_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(RegisterState.last_name)


@dp.message(RegisterState.last_name)
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    await message.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=phone_kb
    )

    await state.set_state(RegisterState.phone)


@dp.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer(
            "Telefonni tugma orqali yuboring."
        )
        return

    await state.update_data(
        phone=message.contact.phone_number
    )

    await message.answer("Yoshingizni kiriting:")
    await state.set_state(RegisterState.age)


@dp.message(RegisterState.age)
async def get_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(
            "Yoshni raqam bilan kiriting."
        )
        return

    await state.update_data(age=message.text)

    await message.answer(
        "Mahallangizni tanlang:",
        reply_markup=mahalla_kb
    )

    await state.set_state(RegisterState.mahalla)


@dp.message(RegisterState.mahalla)
async def get_mahalla(message: Message, state: FSMContext):
    data = await state.get_data()

    add_user(
        user_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        age=data["age"],
        mahalla=message.text
    )

    await message.answer(
        "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!"
    )

    await state.clear()


@dp.message(F.text == "👥 Foydalanuvchilar soni")
async def count_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        f"👥 Jami foydalanuvchilar: {users_count()}"
    )


@dp.message(F.text == "📋 Ishtirokchilar")
async def participants(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users()

    if not users:
        await message.answer("Ro'yxat bo'sh.")
        return

    text = ""

    for i, user in enumerate(users, start=1):
        text += (
            f"👤 #{i}\n"
            f"🆔 ID: {user[0]}\n"
            f"👨 Ism: {user[1]}\n"
            f"👨‍👩‍👦 Familiya: {user[2]}\n"
            f"📞 Telefon: {user[3]}\n"
            f"🎂 Yosh: {user[4]}\n"
            f"🏠 Mahalla: {user[5]}\n"
            f"━━━━━━━━━━━━━━\n"
        )

    for i in range(0, len(text), 4000):
        await message.answer(text[i:i + 4000])
    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users()

    if not users:
        await message.answer("Ro'yxat bo'sh.")
        return

    text = ""

    for i, user in enumerate(users, start=1):
        text += (
            f"{i}. {user[0]} {user[1]}\n"
            f"📞 {user[2]}\n"
            f"🎂 {user[3]}\n"
            f"🏠 {user[4]}\n\n"
        )

    for i in range(0, len(text), 4000):
        await message.answer(text[i:i+4000])


@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "Yuboriladigan xabarni kiriting:"
    )

    await state.set_state(BroadcastState.text)


@dp.message(BroadcastState.text)
async def broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    users = get_users()

    sent = 0
    failed = 0

    for user in users:
        try:
            await bot.send_message(
                chat_id=user[0],
                text=message.text
            )
            sent += 1
            await asyncio.sleep(0.05)

        except Exception:
            failed += 1

    await message.answer(
        f"✅ Yuborildi: {sent}\n❌ Xato: {failed}"
    )

    await state.clear()


@dp.message(Command("id"))
async def my_id(message: Message):
    await message.answer(
        f"Sizning ID: {message.from_user.id}"
    )


async def main():
    me = await bot.get_me()
    print(f"Bot ishga tushdi: @{me.username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())