import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from lexicon.lexicon import LEXICON
from keyboards.keyboards import choice_menu_kb
from handlers.user_handlers import requests_history, FSMData

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    style='{',
    format='{filename}:{lineno} #{levelname:8} [{asctime}] - {name} - {message}'
)

command_router = Router()

@command_router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON['/start'])


@command_router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


@command_router.message(Command(commands='gpt'), StateFilter(default_state))
async def process_gpt_command(message: Message, state: FSMContext):
    await state.set_state(FSMData.start_state)
    await message.answer(
        text=LEXICON['/gpt'],
        reply_markup=choice_menu_kb
    )


@command_router.message(Command(commands='status'))
async def process_status_command(message: Message, state: FSMContext):
    state_data: dict[str, str] = await state.get_data()
    state_cond: str = await state.get_state()
    print(f"State_data: {state_data}")
    print(f"State condition: {state_cond}")
    print(f"Requests history: {requests_history}")


@command_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command(message: Message, state: FSMContext):
    logger.debug(msg='Обработчик команды Отмена')
    requests_history.clear()
    await state.clear()
    await state.set_state(FSMData.start_state)
    await message.answer(
        text=LEXICON['/gpt'],
        reply_markup=choice_menu_kb
    )


@command_router.message(Command(commands='exit'))
async def process_cancel_command(message: Message, state: FSMContext):
    logger.debug(msg='Обработчик команды Выход')
    requests_history.clear()
    await state.clear()
    await message.answer(
        text=LEXICON['/start']
    )
