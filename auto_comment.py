#для работы скрипта нужна библиотека pyrogram, asyncio, datetime.
#названия каналов находятся в файле channels.txt


from pyrogram import Client, types, filters
from datetime import datetime
import re
from pyrogram.errors.exceptions.forbidden_403 import Forbidden

import asyncio

api_id =  #ip с сайта https://my.telegram.org/auth
api_hash = "" #хеш с сайта https://my.telegram.org/auth
phone_number = ""

app = Client('Ваш юзернейм', api_id=api_id, api_hash=api_hash, phone_number=phone_number)

print(f'Приложение успешно запущено {datetime.now()}')

with open('channels.txt', 'r') as file:
    target_channels = [line.strip() for line in file if line.strip()]

async def is_subscribed(client, channel):
    try:
        member = await client.get_chat_member(channel, 'me')
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f'Не удалось проверить статус подписки на {channel}: {e}')
        return False

async def handle_message(client, message: types.Message):
    await asyncio.sleep(3.5)
    dm = await client.get_discussion_message(message.chat.id, message.id)
    message_text = "Текст который отправляется сразу после поста"
    try:
        reply = await dm.reply(message_text)
    except Forbidden:
        await dm.chat.join()
        reply = await dm.reply(message_text)

    await asyncio.sleep(180)
    try:
        await reply.edit_text("Тот на который меняется через 3 минуты")
    except Exception as e:
        print(f'Не удалось изменить сообщение: {e}')

def extract_channel_username(url):
    pattern = r't.me/(joinchat/)?(?P<username>[^/?]+)'
    match = re.search(pattern, url)
    return match.group('username') if match else None

async def main():
    async with app:
        for channel in target_channels:
            if channel.startswith('https://t.me/'):
                channel = extract_channel_username(channel)

            if not await is_subscribed(app, channel):
                try:
                    await app.join_chat(channel)
                    print(f'Успешно присоединились к каналу: {channel}')
                except Exception as e:
                    print(f'Не удалось присоединиться к каналу {channel}: {e}')

            app.add_handler(
                app.on_message(filters.chat(channel))(handle_message)
            )

        while True:
            await asyncio.sleep(60)

if __name__ == '__main__':
    app.run(main())