import sqlalchemy
import pandas as pd
from multiprocessing import Pool
import time
from bs_parser import BrandParser
from datetime import datetime, timedelta
import schedule

def get_data(shop):
    #if shop == 'bs':
    parser = BrandParser()
    data = parser.get_data()
    return data


def main():
    shops = ['bs']
    start = time.time()
    #подключение к БД
    engine = sqlalchemy.create_engine("postgresql://postgres:aaaa@localhost/easybuy")#("postgresql://postgres:rVa_17ll@localhost/test")
    con = engine.connect()
    with Pool(1) as p:
        records = p.map(get_data, shops)
        data = pd.concat(records)
    data['time'] = datetime.utcnow() + timedelta(hours=3)
    data.to_sql('goods', con,  if_exists='append', index=False)
    #data.to_sql('goods', con,schema='easysale', if_exists='append', index=False)

    con.close()
    print(time.time() - start)


schedule.every().day.at("20:24").do(main)
schedule.every().day.at("07:00").do(main)
schedule.every().day.at("09:00").do(main)
schedule.every().day.at("12:00").do(main)
schedule.every().day.at("14:00").do(main)
schedule.every().day.at("16:00").do(main)


if __name__ == "__main__":
    while True:

        schedule.run_pending()
        time.sleep(1)



