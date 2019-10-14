import asyncpg
from datetime import datetime,timedelta
db_data = "postgresql://postgres:aaaa@localhost/easybuy"

async def query_to_db(data):
    conn = await asyncpg.connect(db_data)
    print('Query: user {}, gender {}, cat {} recorded'.format(data['user'],data['gender'],data['cat']))
    await conn.execute('''INSERT INTO queries  VALUES ($1, $2, $3, $4);''',data['user'],datetime.utcnow() + timedelta(hours=3),data['gender'],data['cat'])
    await conn.close()


async def del_user_from_db(user):
    conn = await asyncpg.connect(db_data)
    await conn.execute('''DELETE FROM queries  where "user" = $1;''',user)
    await conn.execute('''DELETE FROM sent  where "user" = $1;''',user)
    await conn.close()
    print('User {} unsubscribed'.format(user))


async def get_user_queries(user):
    conn = await asyncpg.connect(db_data)
    data = await conn.fetch('''SELECT distinct sex,cat FROM queries  where "user" = $1;''', user)
    await conn.close()
    return data

async def get_one_from_all_items(user_id,prev = []):

    conn = await asyncpg.connect(db_data)
    dates = await conn.fetch('''SELECT max("time") "time" FROM goods;''')

    #print(dates[0]['time'],user_id,type(user_id))
    #print(prev)
    if len(dates)>0:
        data = await conn.fetch('''select * from (SELECT distinct q."user" "user",aa.good_id good_id,ref FROM QUERIES q  LEFT JOIN (SELECT good_id,ref,sex,cat FROM goods  where "time" = $1) 
        AA ON q.SEX=AA.SEX AND q.CAT=AA.CAT left join sent sn on  q.user=sn.user and aa.good_id=sn.good_id WHERE AA.CAT IS NOT NULL and sn.user is null) aaa WHERE "user"=$2 and not good_id = any($3::text[]) limit 2;''',dates[0]['time'],user_id,prev)

    else:
        data = []
    await conn.close()

    return data

async def get_user_item():
    conn = await asyncpg.connect(db_data)
    dates = await conn.fetch('''SELECT distinct time FROM goods order by time desc;''')
    if len(dates)>1:
        data = await conn.fetch('''SELECT distinct q."user",aa.good_id,ref FROM
         QUERIES q LEFT JOIN (SELECT good_id,ref,sex,cat FROM goods  where time = $1 except SELECT good_id,ref,sex,cat FROM goods  where time = $2) AA
        ON q.SEX=AA.SEX AND q.CAT=AA.CAT  left join sent sn on  q.user=sn.user and aa.good_id=sn.good_id WHERE AA.CAT IS NOT NULL and sn.user is null limit 5;''',dates[0]['time'],dates[1]['time'])
    else:
        data = []
    await conn.close()

    return data

async def add_user_item_sent(user,item):
    conn = await asyncpg.connect(db_data)
    print('Query: user {}, item {} recorded to sent'.format(user,item))
    await conn.execute('''INSERT INTO sent  VALUES ($1, $2, $3);''', user,item,datetime.utcnow() + timedelta(hours=3))
    await conn.close()


