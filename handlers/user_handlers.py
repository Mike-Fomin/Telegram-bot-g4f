import asyncio
import logging
import requests

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from lexicon.lexicon import LEXICON
from keyboards.keyboards import (choice_menu_kb, send_menu_kb, save_response_kb,
                                 end_part_kb_image, end_part_kb_text, end_part_kb)
from services.services import get_chatgpt_response, run_in_thread
from concurrent.futures import ThreadPoolExecutor


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{filename}:{lineno} #{levelname:8} [{asctime}] - {name} - {message}'
)
user_router = Router()

requests_history: list[dict[str, str]] = []


class FSMDataText(StatesGroup):
    fill_request = State()

class FSMDataImage(StatesGroup):
    fill_request = State()


@user_router.callback_query(F.data == 'get_text_button', StateFilter(default_state))
async def process_choice_button1(callback: CallbackQuery, state: FSMContext):
    logger.debug(msg='Обработчик нажатия кнопки Текст')
    await callback.message.edit_text(
        text=LEXICON['text']
    )
    await state.set_state(FSMDataText.fill_request)


@user_router.callback_query(F.data == 'get_image_button', StateFilter(default_state))
async def process_choice_button2(callback: CallbackQuery, state: FSMContext):
    logger.debug(msg='Обработчик нажатия кнопки Изображение')
    await callback.message.edit_text(
        text=LEXICON['image']
    )
    await state.set_state(FSMDataImage.fill_request)


@user_router.message(StateFilter(FSMDataText.fill_request))
async def process_text_request(message: Message, state: FSMContext):
    logger.debug(msg='Обработчик текстового запроса')
    await state.update_data(text=message.text)
    logger.debug(msg=f"{message.text=}")
    await message.answer(
        text=LEXICON['request_send'],
        reply_markup=send_menu_kb
    )


@user_router.message(StateFilter(FSMDataImage.fill_request))
async def process_image_request(message: Message, state: FSMContext):
    logger.debug(msg='Обработчик запроса изображения')
    await state.update_data(image_request=message.text)
    logger.debug(msg=f"{message.text=}")
    await message.answer(
        text=LEXICON['request_send'],
        reply_markup=send_menu_kb
    )


@user_router.callback_query(F.data == 'send_button', ~StateFilter(default_state))
async def process_send_button(callback: CallbackQuery, state: FSMContext):
    logger.debug(msg='Обработчик нажатия кнопки отправки запроса')
    await callback.answer(text=LEXICON['waiting'])

    state_status: FSMContext = await state.get_state()
    match state_status:
        case FSMDataText.fill_request:
            requests_history.append(
                {
                    'role': 'user',
                    'content': await state.get_value('text')
                }
            )
            logger.debug(msg=f"before {requests_history}")

            await callback.message.delete()

            response: str = get_chatgpt_response(requests_history)
            requests_history.append(
                {
                    'role': 'assistant',
                    'content': response
                }
            )
            logger.debug(msg=f"after {requests_history}")

            await callback.message.answer(
                text=response
            )
            await callback.message.answer(
                text=LEXICON['request_save'],
                reply_markup=save_response_kb
            )
        case FSMDataImage.fill_request:
            image_prompt: str = await state.get_value('image_request')
            await callback.message.delete()

            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                image_resp: str = await loop.run_in_executor(pool, run_in_thread, image_prompt)
                logger.debug(image_resp)

            try:
                image_response = requests.get(image_resp)
                image_response.raise_for_status()

                image_bytes = image_response.content
            except requests.RequestException as ex:
                await callback.message.answer(f"Ошибка: {str(ex)}")
                await callback.answer()
            else:
                sent_photo = await callback.message.answer_photo(
                    photo=BufferedInputFile(image_bytes, 'some.jpg')
                )
                await state.update_data(photo_id=sent_photo.photo[-1].file_id)
                await callback.message.answer(
                    text=LEXICON['request_save'],
                    reply_markup=save_response_kb
                )


@user_router.callback_query(F.data == 'save_button', ~StateFilter(default_state))
async def process_save_button(callback: CallbackQuery, state: FSMContext):
    logger.debug(msg='Обработчик нажатия кнопки Сохранить')

    state_status: FSMContext = await state.get_state()
    match state_status:
        case FSMDataText.fill_request:
            await state.update_data(text_result=requests_history[-1]['content'])
            logger.debug(msg=requests_history[-1]['content'])
            if await state.get_value('photo_result'):
                await callback.message.edit_text(
                    text=LEXICON['end_part'],
                    reply_markup=end_part_kb
                )
            else:
                await callback.message.edit_text(
                    text=LEXICON['text_end_part'],
                    reply_markup=end_part_kb_text
                )
        case FSMDataImage.fill_request:
            await state.update_data(photo_result= await state.get_value('photo_id'))
            logger.debug(msg=await state.get_value('photo_result'))
            if await state.get_value('text_result'):
                await callback.message.edit_text(
                    text=LEXICON['end_part'],
                    reply_markup=end_part_kb
                )
            else:
                await callback.message.edit_text(
                    text=LEXICON['image_end_part'],
                    reply_markup=end_part_kb_image
                )
    await state.set_state(default_state)


@user_router.callback_query(F.data == 'cancel_button', StateFilter(default_state))
async def process_cancel_button(callback: CallbackQuery, state: FSMContext):
    logger.debug(msg='Обработчик нажатия кнопки отмена')
    requests_history.clear()
    await state.clear()
    await callback.message.edit_text(
        text=LEXICON['/gpt'],
        reply_markup=choice_menu_kb
    )


@user_router.callback_query(F.data == 'send_to_chat_button', StateFilter(default_state))
async def process_chat_button(callback: CallbackQuery, state: FSMContext, **workflow_data):
    logger.debug(msg='Обработчик нажатия кнопки отправки в чат')
    text_result: str = await state.get_value('text_result')
    image_result: str = await state.get_value('photo_result')
    if text_result and image_result:
        await callback.bot.send_photo(
            chat_id=f"-100{workflow_data.get('send_chat_id')}",
            photo=image_result,
            caption=text_result
        )
    elif text_result:
        await callback.bot.send_message(
            chat_id=f"-100{workflow_data.get('send_chat_id')}",
            text=text_result
        )
    elif image_result:
        await callback.bot.send_photo(
            chat_id=f"-100{workflow_data.get('send_chat_id')}",
            photo=image_result
        )
    await callback.answer(text=LEXICON['sending'])
    await callback.message.delete()
    await state.clear()
    requests_history.clear()