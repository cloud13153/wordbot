import logging
import asyncio
import random
import googletrans
from googletrans import Translator

import aiogram
from aiogram import Bot, Dispatcher, types, F# executor,
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command

# состояния (временная память)
class FSMpass(StatesGroup):
    word = State()
    level = State()
    wordfrombot = State()


def wordChoice(level, word):
    maybeWords=[]
    file_path = f'words{level}.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.readlines()
            for content in contents:
                content = ((content.split(';'))[0]).lower()
                if word == content[0]:
                    maybeWords.append(content)
            if (len(maybeWords)==0):
                return None
            else:
                return random.choice(maybeWords)
    except FileNotFoundError:
        print("Файл не найден.")

def translate(word):
    translator = Translator()
    translation = translator.translate(word, dest='ru').text
    return translation

def transcription(level, word):
    maybeWords=[]
    file_path = f'words{level}.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.readlines()
            for content in contents:
                content = ((content.split(';')))
                if word==content[0]:
                    return content[2]
    except FileNotFoundError:
        print("Файл не найден.")

def examples(level, word):
    maybeWords=[]
    file_path = f'words{level}.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.readlines()
            for content in contents:
                content = ((content.split(';')))
                if word==content[0]:
                    return content[3]
    except FileNotFoundError:
        print("Файл не найден.")

# кнопки
all_button_1 = 'GO?'
all_button_2 = 'ℹ️Help'

all_button_3 = 'Trans'
all_button_4 = 'Translate'
all_button_5 = 'Examples'
all_button_6 = '⬅️exit'

bstart = [
        [types.KeyboardButton(text=all_button_1)],
        [types.KeyboardButton(text=all_button_2)]
    ]

btranslateTranscriptionExample = [
        [types.KeyboardButton(text=all_button_3),types.KeyboardButton(text=all_button_4)],
        [types.KeyboardButton(text=all_button_5),types.KeyboardButton(text=all_button_6)]
    ]

button_start = ReplyKeyboardMarkup(keyboard=bstart,resize_keyboard=True)
translateTranscriptionExample = ReplyKeyboardMarkup(keyboard=btranslateTranscriptionExample,resize_keyboard=True)

TOKEN = '7126464716:AAFeJyom835xaIhcM4n2X6NYmrP3RSihsso'

bot = Bot(token=TOKEN)# Объект бота
storage=MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def сmd_start(message: types.Message):
    await message.answer('🔈 Hello, dear student.\nI will help you learn english\n'
                         '\n💬 To find out my commands, click on the\nℹ️Help'
                                                    , reply_markup=button_start)

# Хэндлеры на команду /help
@dp.message(F.text == "ℹ️Help")
async def сmd_help(message: types.Message):
    await message.reply('My commands:\n'
                        'There are not help'
                    , reply_markup=button_start, parse_mode='html')

# Хэндлеры на команду /GO
@dp.message(F.text == "GO?")
async def сmd1_go(message: types.Message, state: FSMContext):
    msg1 = await message.answer("Select difficulty level!"
                                ,reply_markup=ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='1'),types.KeyboardButton(text='2'),types.KeyboardButton(text='3')]],resize_keyboard=True))
    await state.set_state(FSMpass.level)
@dp.message(StateFilter(FSMpass.level))
async def сmd2_go(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        answer = int(answer)
        if 1<= answer <=3:
            await state.update_data(level=answer)
            msg2 = await message.answer("You first! \n"
                                    "Submit me word: ",reply_markup=ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=all_button_6)]],resize_keyboard=True))
            await state.set_state(FSMpass.word)
        else:
            await message.answer('There are only three difficulty levels!!', reply_markup=button_start)
            await state.clear()
    except Exception:
        await message.answer('Only numbers can be entered here!!!', reply_markup=button_start)
        await state.clear()
@dp.message(StateFilter(FSMpass.word))
async def сmd3_go(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    level = data.get('level')
    wordfrombot = data.get('wordfrombot')
    if answer=='⬅️exit':
        await state.clear()
        msg2 = await message.answer('Word game is closed!',reply_markup=button_start)
    elif answer == 'Trans':
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f'Transcription-> {transcription(level, str(wordfrombot))}',reply_markup=translateTranscriptionExample)
    elif answer == 'Examples':
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f'Examples-> {examples(level, str(wordfrombot))}',reply_markup=translateTranscriptionExample)
    elif answer == 'Translate':
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await message.answer(f'Translate-> {translate(str(wordfrombot))}',reply_markup=translateTranscriptionExample)
    else:
        wordfrombot = wordChoice(level, str(answer[len(answer)-1]))
        if (wordfrombot==None):
            msg2 = await message.answer("You defeated me! :((((\n"
                                        "Youre are too strong...",reply_markup=button_start)
            await state.clear()
        else:
            await state.update_data(wordfrombot=wordfrombot)
            msg2 = await message.answer(str(wordfrombot),reply_markup=translateTranscriptionExample)



# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())