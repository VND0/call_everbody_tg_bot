import json
import asyncio
from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message
from time import sleep
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.exceptions import TelegramBadRequest
import make_logs


bot_logger = make_logs.Logger()

with open("settings.json", "r") as f:
    SETTINGS = json.load(f)
bot = Bot(token=SETTINGS["API_KEY"])
dp = Dispatcher()


def read_users_from_chat(chat_id: str) -> list:
    with open("registered_users.json", "r") as f:
        db = json.load(f)
    try:
        required_chat_users = db[chat_id]
    except KeyError:
        return []

    bot_logger.make_info_log("Получен список пользователей из базы данных.")
    return required_chat_users


async def register_new_user(chat_id: str, user_id: str) -> None:
    with open("registered_users.json", "r") as f:
        db = json.load(f)

    if chat_id in db.keys():
        db[chat_id].append(user_id)
    else:
        db[chat_id] = [user_id]

    with open("registered_users.json", "w") as f:
        f.write(json.dumps(db, indent=4))

    bot_logger.make_info_log(f"Пользователь {user_id} добавлен в базу данных для чата {chat_id}.")


@dp.message(Command("start", "help"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет. Этот бот должен тегать всех при использовании команды `/call` или `/all`",
        disable_notification=True
    )
    await message.answer(
        "Чтобы бот узнал о вас, введите `/register` или `/add`. Без этого работать не будет.",
        disable_notification=True
    )

    bot_logger.make_info_log(f"Пользователь @{message.from_user.username} отправил команду /start или /help.")


@dp.message(Command("call", "all"))
async def tagger_handler(message: Message) -> None:
    msg_to_tag_id = str(message.message_id)
    chat_id = str(message.chat.id)
    user_id = "@" + message.from_user.username
    users_to_tag = read_users_from_chat(chat_id)

    if users_to_tag:
        try:
            users_to_tag.remove(user_id)
        except ValueError:
            bot_logger.make_warn_log(f"Пользователь {user_id} призвал других, хотя сам не был зарегистрирован.")
            await register_new_user(chat_id, user_id)
            bot_logger.make_info_log(f"Пользователь {user_id} зарегистрирован в чате {chat_id}")
    else:
        await message.answer(
            text="Ай-яй! Никто не зарегистрировался. Кого упоминать-то?",
            disable_notification=True
        )
        bot_logger.make_warn_log(f"В чате {chat_id} была совершена попытка призыва, но никто не зарегистрировался.")
        await message.answer(
            text=f"Пользователь {user_id} добавлен в список для упоминания.",
            disable_notification=True
        )
        await register_new_user(chat_id=chat_id, user_id=user_id)
        bot_logger.make_info_log(f"Пользователь {user_id} зарегистрирован в чате {chat_id}")
        return

    normal_part = f"Пользователь {user_id} призывает всех участников чата!"
    tag_part = " ".join(users_to_tag)

    try:
        msg_tagger = await message.answer(
            text=normal_part + "\n" + tag_part,
            reply_to_message_id=int(msg_to_tag_id),
        )
        bot_logger.make_info_log(f"Пользователь {user_id} призвал остальных участников чата.")
    except TelegramBadRequest:
        bot_logger.make_warn_log(f"Не найдено сообщение {msg_to_tag_id}. Отправлен призыв без ответ.")
    sleep(3)
    msg_tagger_id = msg_tagger.message_id
    # В данном случае исключение мб вызвано либо отсутствием интернета (тогда в принципе упадет все, поэтому все равно),
    # либо отсутствием сообщения, на которое отвечать (тогда бот не падает, сообщение просто отправляется).
    # Так или иначе, переменная с id сообщения будет существовать.

    try:
        await bot(EditMessageText(text=normal_part, chat_id=chat_id, message_id=int(msg_tagger_id)))
    except TelegramBadRequest:
        bot_logger.make_warn_log(f"Редактирование сообщения пользователя {user_id} в чате {chat_id} не дало результатов.")


@dp.message(Command("register", "add"))
async def registration_handler(message: Message) -> None:
    user_id = "@" + str(message.from_user.username)
    chat_id = str(message.chat.id)

    users_of_chat = read_users_from_chat(chat_id)
    if user_id in users_of_chat:
        await message.answer(
            text="По данным бота вы уже добавились, а дважды добавляться нельзя!",
            disable_notification=True
        )
        bot_logger.make_warn_log(f"Пользователем {user_id} в чате {chat_id} совершена попытка повторной регистрации.")
        return

    await register_new_user(chat_id=chat_id, user_id=user_id)
    await message.answer(
        text=f"Готово! Пользователь {user_id} добавлен.",
        disable_notification=True
    )
    bot_logger.make_info_log(f"Пользователь {user_id} добавлен в базу данных для чата {chat_id}.")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
