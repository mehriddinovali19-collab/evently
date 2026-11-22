from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject, Command
from bot.api_client import api_client

router = Router()

@router.message(CommandStart())
async def command_start(message: types.Message, command: CommandObject):
    token = command.args

    if not token:
        await message.answer(f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
            "👋 <b>Evently Telegram Boti</b>ga xush kelibsiz!\n\n"
            "Profilingizni sayt bilan bog'lash uchun, veb-saytimizdagi shaxsiy profilingizga kiring "
            "va <b>'Telegram bilan bog'lash'</b> tugmasini bosing.\n\n"
            "Agar akkauntingiz allaqachon ulangan bo'lsa, tadbirlaringizni ko'rish uchun /my_events buyrug'ini yuboring.")
        return 

    response = await api_client.confirm_telegram_account(token=token, chat_id=message.chat.id)

    if response is None:
        await message.answer("⚠️ Server bilan bog'lanishda nosozlik yuz berdi. Backend ishlayotganligini tekshiring.")
        return

    if response.status_code == 200:
        data = response.json()
        email = data.get('email', '')
        full_name = data.get('full_name', '')
        await message.answer(
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            f"Hurmatli <b>{full_name or email}</b>, profilingiz Evently tizimiga muvaffaqiyatli bog'landi!\n\n"
            "Endi siz:\n"
            "• Tadbirlarga ro'yxatdan o'tganingizda darhol tasdiq xabarnomasini olasiz\n"
            "• Tadbir boshlanishiga 24 soat qolganda eslatmalar qabul qilasiz\n"
            "• /my_events buyrug'i orqali istalgan vaqtda barcha chiptalaringizni ko'ra olasiz."
        )

    elif response.status_code == 404:
        await message.answer(
            "❌ <b>Havola eskirgan yoki yaroqsiz!</b>\n\n"
            "Ushbu havoladan avval foydalanilgan yoki muddati tugagan. Iltimos, saytdan yangi havola oling."
        )
    else:
        await message.answer("⚠️ Akkauntni bog'lashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.") 


@router.message(Command("my_events"))
async def get_my_event(message: types.Message):
    response = await api_client.get_user_events(chat_id= message.chat.id)

    if response is None:
        await message.answer("⚠️ Ma'lumotlarni olishda server bilan ulanish nosozligi.")
        return

    if response.status_code == 404:
        await message.answer(
            "❌ <b>Akkaunt bog'lanmagan!</b>\n\n"
            "Sizning Telegram hisobingiz tizimdagi hech qaysi profilga ulanmagan.\n"
            "Iltimos, saytdan profilingizga kiring va 'Telegram bilan bog'lash' tugmasini bosing."
        )

        return 

    if response.status_code != 200:
        await message.answer("⚠️ Tadbirlarni yuklashda xatolik yuz berdi.")
        return

    data = response.json()
    events = data.get("events", [])

    if not events:
        await message.answer(f"👤 Hurmatli <b>{data.get('full_name') or data.get('user_email')}</b>,\n\n"
            "Hozirda siz ro'yxatdan o'tgan faol tadbirlar mavjud emas.")
        return
    text = f"📋 <b>Sizning tadbirlaringiz ({len(events)} ta):</b>\n\n"
    for idx, ev in enumerate(events, 1):
        text += (
            f"<b>{idx}. {ev['event_title']}</b>\n"
            f"🔹 Turi: {ev['event_type'].capitalize()}\n"
            f"🗓 Sana: {ev['start_at']}\n"
            f"📍 Manzil: {ev['location']}\n"
            f"🔖 Chipta holati: <i>{ev['status']}</i>\n"
            "─────────────────\n"
        )
    await message.answer(text)