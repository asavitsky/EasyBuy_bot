import asyncio
from telethon import TelegramClient
import logging
import handlers
from db_comm import get_user_item,add_user_item_sent


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

api_id = 
api_hash = ''

loop = asyncio.new_event_loop()
bot = TelegramClient('bot',  api_id, api_hash, proxy=None,loop=loop).start(bot_token='')


async def notify():
    while True:
        user_item = await get_user_item()
        if user_item:
            for id in range(len(user_item)):
                await bot.send_message(int(user_item[id]['user']),user_item[id]['ref'])
                await add_user_item_sent(user_item[id]['user'], user_item[id]['good_id'])

        await asyncio.sleep(5)


if __name__ == '__main__':
    loop.create_task(notify())
    bot.add_event_handler(handlers.start)
    bot.add_event_handler(handlers.all_goods)
    bot.add_event_handler(handlers.params)
    bot.add_event_handler(handlers.handler)
    bot.add_event_handler(handlers.subsc)
    bot.add_event_handler(handlers.cancel_subsc)
    bot.run_until_disconnected()
