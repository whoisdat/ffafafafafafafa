import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# Настройки
TOKEN = "7908748621:AAH0XS-abiMUPakjefaVlOommENiCZAcLqA"
GROUP_CHAT_ID = -1002624869413  # ID твоей приватной группы
CURRENCY = "XTR"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(F.text == "/start")
async def command_start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💫 Telegram Stars", callback_data="pay_stars")]
    ])
    await message.answer("Monthly subscription", reply_markup=keyboard)

@dp.callback_query(F.data == "pay_stars")
async def handle_payment_callback(callback_query):
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="30-Day Subscription",
        description="Pay and get a link",
        payload="access_to_private",
        currency=CURRENCY,
        prices=[LabeledPrice(label="XTR", amount=1)]  # 1 XTR для теста
    )
    await callback_query.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    logging.info(f"Pre-checkout query: {pre_checkout_query}")
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    logging.info(f"Получена оплата: {message.successful_payment}")
    if message.successful_payment.invoice_payload == "access_to_private":
        try:
            link = await bot.create_chat_invite_link(
                chat_id=GROUP_CHAT_ID,
                member_limit=1,
                name=f"Invite for {message.from_user.username or message.from_user.id}"
            )
            await message.answer(f"Твоя ссылка: (Your link:)\n{link.invite_link}")
        except Exception as e:
            await message.answer("Ошибка при создании ссылки. Свяжись с поддержкой.")
            logging.error(f"Ошибка при создании ссылки: {e}")
    else:
        await message.answer("Неизвестный тип оплаты.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
