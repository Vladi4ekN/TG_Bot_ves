from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await main_menu(message)


async def main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Рассчитать'))
    keyboard.add(types.KeyboardButton('Информация'))

    await message.reply("Выберите опцию:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'рассчитать')
async def show_inline_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'))
    keyboard.add(types.InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas'))

    await message.reply("Выберите опцию:", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_message = (
        "Формула Миффлина-Сан Жеора:n"
        "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5n"
        "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formula_message)


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.message.answer('Введите свой возраст:')


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await UserState.growth.set()
    await message.reply('Введите свой рост (в см):')


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await UserState.weight.set()
    await message.reply('Введите свой вес (в кг):')


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()

    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    # Расчет BMR (Basal Metabolic Rate)
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.reply(f'Ваша норма калорий: {bmr:.2f} ккал.')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
