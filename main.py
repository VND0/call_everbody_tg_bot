import json
import asyncio
from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message
from time import sleep
from aiogram.methods.edit_message_text import EditMessageText


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
            await register_new_user(chat_id, user_id)
    else:
        await message.answer(
            text="Ай-яй! Никто не зарегистрировался. Кого упоминать-то?",
            disable_notification=True
        )
        await message.answer(
            text=f"Пользователь {user_id} добавлен в список для упоминания.",
            disable_notification=True
        )
        await register_new_user(chat_id=chat_id, user_id=user_id)
        return

    normal_part = f"Пользователь {user_id} призывает всех участников чата!"
    tag_part = " ".join(users_to_tag)

    msg_tagger = await message.answer(
        text=normal_part + "\n" + tag_part,
        reply_to_message_id=int(msg_to_tag_id),
    )
    sleep(3)
    msg_tagger_id = msg_tagger.message_id
    await bot(EditMessageText(text=normal_part, chat_id=chat_id, message_id=int(msg_tagger_id)))


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
        return

    await register_new_user(chat_id=chat_id, user_id=user_id)
    await message.answer(
        text=f"Готово! Пользователь {user_id} добавлен.",
        disable_notification=True
    )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
