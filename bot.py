import asyncio
import logging
import sys
import requests
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import TOKEN, kjh2ru_url, ru2kjh_url

form_router = Router()


class Form(StatesGroup):
    task = State()
    user_input = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.task)
    await message.answer(
        "Изеннер!\nНиме идерге сағынчазар?\nЧто хотите сделать?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Перевести текст с хакасского на русский")],
                [KeyboardButton(text="Перевести текст с русского на хакасский")],
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(Form.task)
async def process_task(message: Message, state: FSMContext) -> None:
    data = await state.update_data(task=message.text)
    task = data['task']

    if task == 'Перевести текст с хакасского на русский':
        await state.set_state(Form.user_input)
        await message.answer("Введите текст на хакасском языке", reply_markup=ReplyKeyboardRemove())
    elif task == 'Перевести текст с русского на хакасский':
        await state.set_state(Form.user_input)
        await message.answer("Введите текст на русском языке", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Некорректная команда", reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.user_input)
async def process_user_input(message: Message, state: FSMContext) -> None:
    data = await state.update_data(task=message.text)
    task = data['task']
    user_input = data['user_input']

    if task == 'Перевести текст с хакасского на русский':
        await translate_kjh2ru(message=message, state=state, text=user_input)
    elif task == 'Перевести текст с русского на хакасский':
        await translate_kjh2ru(message=message, state=state, text=user_input)
    else:
        await message.answer("Некорректная команда", reply_markup=ReplyKeyboardRemove())


async def translate_kjh2ru(message: Message, state: FSMContext, text: str) -> None:
    translation = requests.get(kjh2ru_url, params={'text': text}).text
    await message.reply(text=translation, reply_markup=ReplyKeyboardRemove())


async def translate_ru2kjh(message: Message, state: FSMContext, text: str) -> None:
    translation = requests.get(ru2kjh_url, params={'text': text}).text
    await message.reply(text=translation, reply_markup=ReplyKeyboardRemove())


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
