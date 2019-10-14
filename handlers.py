from telethon import events
from telethon import Button
from datetime import datetime, timedelta
from db_comm import query_to_db,del_user_from_db,get_user_queries,get_one_from_all_items

genders = {b'1':'m',b'2':'w'}
genders_ru ={'m':'Мужчины','w':'Женщины'}
goods_ru = {'1':'Футболки','2':'Кроссовки','3':'Рубашки'}
users = {}
prev_good = {}

def generate_keyboard(tp,data):
    return [Button.inline(txt, '{}_{}'.format(i+1,tp)) for i,txt in enumerate(data)]


def generate_ans(data):
    answer = ''
    for i in range(len(data)):
        answer += 'Для {}, категория: {}\n'.format(genders_ru[data[i]['sex']],goods_ru[data[i]['cat']])
    return answer


@events.register(events.NewMessage(pattern='/start'))
async def start(event):
    bot = event.client
    markup = bot.build_reply_markup([[Button.text('Ввести данные для поиска', resize=True, single_use=False),
                                     Button.text('Все подходящие товары', resize=True, single_use=False)],[Button.text('Мои запросы', resize=True, single_use=False), Button.text('Отписаться', resize=True, single_use=False)]])
    await bot.send_message(event.chat_id,'Привет!\nЯ умею искать вещи по выгодной цене',buttons=markup)
    raise events.StopPropagation


@events.register(events.NewMessage(pattern='Все подходящие товары'))
async def all_goods(event):
    bot = event.client
    chat_id = event.chat_id
    prev_good[chat_id] = {}
    prev_good[chat_id]['good_id'] = []
    prev_good[chat_id]['ref'] = []
    user_item = await get_one_from_all_items(str(chat_id),[])
    if user_item:
        if len(user_item)> 1:
            markup = bot.build_reply_markup(Button.inline('Следующий','1_all'))
        else:
            markup = None
        await bot.send_message(chat_id, user_item[0]['ref'], buttons=markup)
        prev_good[chat_id]['good_id'].append(str(user_item[0]['good_id']))
        prev_good[chat_id]['ref'].append(user_item[0]['ref'])
    else:
        await bot.send_message(chat_id, 'Товаров, соответствующих вашему запросу не найдено(')

    raise events.StopPropagation

@events.register(events.NewMessage(pattern='Ввести данные для поиска'))
async def params(event):
    bot = event.client
    markup = bot.build_reply_markup(generate_keyboard('sex',['Мужчины','Женщины']))
    await bot.send_message(event.chat_id, 'Для кого вы ищете вещь?',buttons=markup)
    raise events.StopPropagation


@events.register(events.CallbackQuery)
async def handler(event):
    bot = event.client
    chat_id = event.chat_id
    data = event.data.split(b'_')
    if data[1] == b'sex':
        await event.delete()
        users[chat_id] = {'user':str(chat_id),'gender':str(genders[data[0]])}
        markup = bot.build_reply_markup(generate_keyboard('cat',['Футболки','Кроссовки','Рубашки']))
        await bot.send_message(chat_id, 'Какой категории товар вам нужен?\n', buttons=markup)

    elif data[1] == b'cat':
        await event.delete()
        markup = bot.build_reply_markup([Button.inline('Начать поиск', '1_src')])
        users[chat_id]['cat'] = str(data[0],'utf-8')
        await bot.send_message(chat_id,'Подтвердите параметры поиска:\nдля {} \nкатегория: {}'.format(genders_ru[users[chat_id]['gender']].lower(),goods_ru[users[chat_id]['cat']].lower()),buttons=markup)

    elif data[1] == b'src':
        await event.delete()
        await bot.send_message(event.chat_id,'Мы ищем подходящий вам вариант.\nКак только найдем что-то подходящее дам знать)')
        await query_to_db(users[chat_id])

    elif data[1] == b'all':
        #print(prev_good)
        await event.delete()
        if data[0] == b'1':

            user_item = await get_one_from_all_items(str(chat_id),prev_good[chat_id]['good_id'])
            if len(user_item) > 1:
                markup = bot.build_reply_markup([Button.inline('Предыдущий', '0_all'),Button.inline('Следующий', '1_all')])
            elif len(user_item) == 1:
                markup = bot.build_reply_markup([Button.inline('Предыдущий', '0_all')])
            else:
                markup = None
            await bot.send_message(chat_id, user_item[0]['ref'], buttons=markup)

            prev_good[chat_id]['good_id'].append(str(user_item[0]['good_id']))
            prev_good[chat_id]['ref'].append(user_item[0]['ref'])


        if data[0] == b'0':
            len_it = len(prev_good[chat_id]['good_id'])
            if len_it >= 2:
                prev_good[chat_id]['ref'].pop()
                prev_good[chat_id]['good_id'].pop()
                user_ref = prev_good[chat_id]['ref'].pop()
                prev_good[chat_id]['good_id'].pop()

                if len_it == 2 :
                    markup = bot.build_reply_markup([Button.inline('Следующий', '1_all')])
                elif len_it > 2:
                    markup = bot.build_reply_markup([Button.inline('Предыдущий', '0_all'), Button.inline('Следующий', '1_all')])

                await bot.send_message(chat_id, user_ref, buttons=markup)


    raise events.StopPropagation


@events.register(events.NewMessage(pattern='Мои запросы'))
async def subsc(event):
    bot = event.client
    user = event.chat_id
    queries = await get_user_queries(str(user))
    answer = generate_ans(queries).lower()
    await bot.send_message(user,'Ваши запросы:\n'+answer)
    raise events.StopPropagation


@events.register(events.NewMessage(pattern='Отписаться'))
async def cancel_subsc(event):
    bot = event.client
    user = event.from_id
    await del_user_from_db(str(user))
    await bot.send_message(event.chat_id, 'Подписка отменена')
    raise events.StopPropagation
