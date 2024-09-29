from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from model import answer_question

bot = Bot('7670368440:AAFHkJEP3WkMj8NabxjzHfackMnJ-6XqHR4')
dp = Dispatcher()

class Form(StatesGroup):
    state_generate = State()

async def main():
    await dp.start_polling(bot)

@dp.message(Command('start'))
async def start(msg: Message):
    await msg.answer("""
Привет👋
Я интеллектуальный помощник оператора службы поддержки 🗣
Просто задайте мне вопрос, который вас волнует...                     
""")

@dp.message()
async def callback_text(msg: Message, state: FSMContext):
    text = msg.text
    try:
        if len(text) <= 2000:
            data = await state.get_state()
            if data is None:
                await state.set_state(Form.state_generate)
                deleted_msg = await msg.answer("Ваш запрос в обработке, пожалуйста, подождите 🔄")
                returned_text = answer_question(text)#Запуск нейронки с передачей текстового запроса пользователя
                await deleted_msg.delete()
                await msg.reply(returned_text)#возврат ответа нейронки
                await state.clear()
            else:
                await msg.reply("Вы уже сделали запрос, дождитесь ответа...")
        else:
            await msg.answer("Ваше сообщение содержит больше 2000 символов❗️")
    except:
        await msg.answer("Необходим текстовый формат запроса❗️")

if __name__ == '__main__':
    asyncio.run(main())