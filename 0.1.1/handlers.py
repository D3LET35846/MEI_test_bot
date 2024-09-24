import os
from aiogram import Bot
from aiogram.types import Message,  InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from datetime import datetime
import re
from config import CHANNEL_USERNAME
from database import User, SessionLocal

router = Router()

class LetterState(StatesGroup):
    writing_letter = State()
    entering_name = State()
    entering_group = State()
    entering_send_date = State()
    entering_send_after = State()

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

async def delete__message(bot: Bot, user_id: int, chat_id: int):
    try:
        await bot.delete_message(chat_id=user_id, message_id=chat_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@router.message(Command(commands=['start']))
async def send_start(message: Message):
    inline_k_sub = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Telegram", url="https://t.me/MPEIcompetence"),
             InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/mpeicompetence")],
            [InlineKeyboardButton(text="Проверить подписки", callback_data="check_sub")]
        ]
    )
    await message.answer("⚡️Здравствуйте! Чтобы продолжить, подпишитесь на наши страницы в VK и TG.⚡️", reply_markup=inline_k_sub)
    #await delete__message(bot,user_id=message.chat.id,chat_id=message.message_id)


@router.callback_query()
async def handle_button(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.message.chat.id  # Получение user_id из callback запроса
    chat_id = callback.message.message_id
    inline_test_sub = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Telegram", url="https://t.me/MPEIcompetence"),
             InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/mpeicompetence")],
            [InlineKeyboardButton(text="Проверить подписки", callback_data="check_sub")]
        ]
    )
    if callback.data == "check_sub":
        if await check_subscription(bot, user_id):
            async with SessionLocal() as session:
                async with session.begin():
                    user = (await session.execute(select(User).filter_by(user_id=user_id))).scalar()
                    if not user:
                        user = User(user_id=user_id, is_subscribed=True)
                        session.add(user)
                    else:
                        user.is_subscribed = True
                    await session.commit()

            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Центр развития", callback_data="Developmet_C"),
                     InlineKeyboardButton(text="Центр мероприятий", callback_data="Event_C")],
                    [InlineKeyboardButton(text="Центр связей", callback_data="Communication_C"),
                     InlineKeyboardButton(text="Центр компетенций", callback_data="Competence_C")]
                ]
            )
            await callback.message.answer(f"Подписка потвердилась, меню!", reply_markup=inline_k_menu)
            await delete__message(bot,user_id,chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)
        await callback.answer()



    elif callback.data == "Menu":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Центр развития", callback_data="Developmet_C"),
                     InlineKeyboardButton(text="Центр мероприятий", callback_data="Event_C")],
                    [InlineKeyboardButton(text="Центр связей", callback_data="Communication_C"),
                     InlineKeyboardButton(text="Центр компетенций", callback_data="Competence_C")]
                ]
            )
            await callback.message.answer(f"Меню! {user_id}", reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)





    elif callback.data == 'Developmet_C':
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Письмо в будущее", callback_data="Letter_Future"),
                     InlineKeyboardButton(text="Записаться на ИТР", callback_data="Sign_ITR")],
                    [InlineKeyboardButton(text="Вернуться в меню", callback_data="Menu")]
                ]
            )

            await callback.message.answer(
                text="""В этом разделе вы найдёте наши инструменты для личностного роста. Здесь вы можете написать письмо самому себе в будущее (попробуйте, это невероятно!), а также записаться на консультацию для создания индивидуальной траектории развития.
    
    Команда ЦК продолжает работать над совершенствованием раздела, но основные возможности уже доступны""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Letter_Future":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Через 4 года (бакалавриат) 🎓", callback_data="Letter_Future_4"),
                     InlineKeyboardButton(text="Через 5 лет (специалитет) 🎓", callback_data="Letter_Future_5")],
                    [InlineKeyboardButton(text="Вернуться назад", callback_data="Developmet_C")]
                ]
            )
            await callback.message.answer(
                text="""Как путешествовать во времени? ⏳
    Как формировать свой успех?
    Написать письмо на выпускной самому себе! 📝
    Когда прислать вам письмо? 🦉📨""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Letter_Future_4" or callback.data == "Letter_Future_5":
        if await check_subscription(bot, user_id):
            age = int(callback.data.split("_")[2])
            await state.update_data(send_after=age)
            await state.set_state(LetterState.writing_letter)
            await callback.message.answer(
                text=f"""Представьте, какое будущее вас ждет в конце обучения. О чем вы мечтаете сейчас? Какие советы дали бы себе будущему? Каким человеком хотите стать за время обучения в МЭИ?
    Пришлем вам письмо через {age} лет! Напишите письмо:""")
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Event_C":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Скилл-паспорта", callback_data="Letter_Future"),
                     InlineKeyboardButton(text="Книжный клуб", callback_data="Sign_ITR")],
                    [InlineKeyboardButton(text="Дебатный центр", callback_data="Letter_Future"),
                     InlineKeyboardButton(text="Курсы РСВ", callback_data="Sign_ITR")],
                    [InlineKeyboardButton(text="Лаборатория технотворчеста", callback_data="Letter_Future"),
                     InlineKeyboardButton(text="Антинаучная конференция", callback_data="Sign_ITR")],
                    [InlineKeyboardButton(text="Учёба", callback_data="1")],
                    [InlineKeyboardButton(text="Вернуться в меню", callback_data="Menu")]
                ]
            )
            await callback.message.answer("Что такое центр меропр и выберите категории", reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Communication_C":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Согласен участвовать", callback_data="Agree_Participate"),
                     InlineKeyboardButton(text="Написать вопрос руководителю", callback_data="Write_head")],
                    [InlineKeyboardButton(text="Вернуться в меню", callback_data="Menu")]
                ]
            )
            await callback.message.answer(
                text="Каждую неделю я буду предлагать тебе для встречи интересного человека, случайно выбранного среди других студентов МЭИ. Чтобы принять участие во встречах, нужно заполнить анкету.",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Competence_C":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Базовые компетенции", callback_data="Basic_competencies"),
                     InlineKeyboardButton(text="Дополнительные компетенции", callback_data="Additional_competencies")],
                    [InlineKeyboardButton(text="Как развить свои компетенции?", callback_data="Develop_competencies")],
                    [InlineKeyboardButton(text="Вернуться в меню", callback_data="Menu")]
                ]
            )
            await callback.message.answer(
                text="""Центр Компетенций НИУ "МЭИ" это:
    
    – место осознанного взаимодействия студентов с потенциальными работодателями при поддержке университета, Министерства науки и высшего образования РФ и АНО "Россия — страна возможностей";
    – комфортная среда для подбора квалифицированных кадров для работодателей;
    – площадка для развития кадрового потенциала университета (образовательных программ, преподавательского состава и административного персонала).
    
    Здесь ты сможешь вместе с нами создать наилучший вариант своего будущего!""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Basic_competencies":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Вернуться назад", callback_data="Competence_C")]
                ]
            )
            await callback.message.answer(
                text="""Базовые компетенции состоят из таких компетенций как:
    
    – анализ информации: способность анализировать и работать с различными видами информации, устанавливать связи между разрозненными данными.
    – ориентация на результат: принятие ответственности за достижение поставленных целей, постановка амбициозных задач.
    – партнерство: развитие навыков сотрудничества, выявление и учёт потребностей и интересов других участников.
    – планирование: разработка комплексного плана действий для выполнения задач, определение приоритетов, оценка ресурсов и сроков.
    – следование правилам: соблюдение существующих норм, регламентов, процедур и политик.
    – стрессоустойчивость: сохранение продуктивности в сложных ситуациях.""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Additional_competencies":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Вернуться назад", callback_data="Competence_C")]
                ]
            )
            await callback.message.answer(
                text="""Дополнительные компетенции состоят из таких компетенций как:
    
    – лидерство: принятие на себя ответственности за результаты работы других, мотивация людей и координирование их усилий для достижения целей.
    – саморазвитие: стремление к постоянному повышению своего профессионализма и активная работа над развитием своих навыков.
    – клиентоориентированность: выявление потребности клиента, действие исходя из его ожиданий и поиск баланса между интересами компании и потребностями заказчиков.
    – эмоциональный интеллект: определение своих эмоций и эмоций других людей, а также взаимодействие с учётом индивидуальных особенностей окружающих.
    – коммуникабельность: склонность к дружелюбному и социально активному поведению, поиск новых знакомств и впечатлений, расширение своих интересов и привлечение внимания к себе.
    – пассивный словарный запас: наличие слов, которые человек узнает в процессе обучения и понимает их значение, но не использует в спонтанной речи.""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

    elif callback.data == "Develop_competencies":
        if await check_subscription(bot, user_id):
            inline_k_menu = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Вернуться назад", callback_data="Competence_C")]
                ]
            )
            await callback.message.answer(
                text="""Для того, чтобы развить свои компетенции, тебе нужно:
    
    1. Определить свой путь развития, пройдя тесты на сайте (https://softskills.rsv.ru/).
    2. Изучить бесплатные онлайн-курсы на платформе "Россия — страна возможностей".
    3. Принять участие в мероприятиях Центра Компетенций НИУ "МЭИ".
    4. Стать участником школы амбассадоров "Россия — страна возможностей"
    5. Открыть для себя "Профориентационные поездки".
    6. Присоединиться к выездным программам "На одной волне со студентами".""",
                reply_markup=inline_k_menu)
            await delete__message(bot, user_id, chat_id)
        else:
            await callback.message.answer("Не найдены подписки!",reply_markup=inline_test_sub)
            await delete__message(bot,user_id,chat_id)

@router.message(LetterState.writing_letter)
async def handle_write_letter(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    letter_text = message.text

    await state.update_data(letter_text=letter_text)
    await state.set_state(LetterState.entering_name)
    await message.answer("Введите ваше имя:")

@router.message(LetterState.entering_name)
async def handle_entering_name(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    await state.update_data(name=message.text)
    await state.set_state(LetterState.entering_group)
    await message.answer("Введите вашу группу (например, ЭЛ-03-24):")

@router.message(LetterState.entering_group)
async def handle_entering_group(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    group_pattern = r"^[A-Za-zА-Яа-я]{2,3}-\d{2}-\d{2}$"
    if not re.match(group_pattern, message.text):
        await message.answer("Неверный формат группы. Пожалуйста, введите группу в формате (например, ЭЛ-03-24).")
        return

    await state.update_data(group=message.text)
    await state.set_state(LetterState.entering_send_date)
    await message.answer("Введите дату написания письма (в формате ГГГГ-ММ-ДД):")

@router.message(LetterState.entering_send_date)
async def handle_entering_send_date(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    try:
        send_date = datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data(send_date=send_date)
        data = await state.get_data()

        user_id = message.from_user.id
        letter_text = data['letter_text']
        name = data['name']
        group = data['group']
        send_date = data['send_date']
        send_after = data['send_after']

        # Create the directory if it doesn't exist
        letter_directory = "base"
        os.makedirs(letter_directory, exist_ok=True)

        filename = f"{name}, {group}, {send_date.strftime('%Y-%m-%d')}, Через {send_after} лет.txt"
        filepath = os.path.join(letter_directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(letter_text)

        async with SessionLocal() as session:
            async with session.begin():
                user = (await session.execute(select(User).filter_by(user_id=user_id))).scalar()
                if not user:
                    user = User(user_id=user_id, name=name, group=group, send_date=send_date, send_after=send_after, letter_filename=filename)
                    session.add(user)
                else:
                    user.name = name
                    user.group = group
                    user.send_date = send_date
                    user.send_after = send_after
                    user.letter_filename = filename
                await session.commit()

        inline_k_menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться в меню", callback_data="Menu")],
                [InlineKeyboardButton(text="Переделать письмо", callback_data="Letter_Future")]
            ]
        )
        await message.answer("Ваше письмо сохранено. Мы пришлем его вам в будущее!", reply_markup=inline_k_menu)
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД:")
