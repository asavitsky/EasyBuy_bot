import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

CATS = ['Кроссовки','Футболки','Рубашки']
SEX =['Женский','Мужской']
CATS_DICT ={'Футболки':'1','Кроссовки':'2','Рубашки':'3'}
SEX_DICT = {'Женский':'w','Мужской':'m'}


class BrandParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'})
        self.url = 'https://brandshop.ru/sale/?limit=240&mfp=17-pol[{}],31-kategoriya[{}]&page={}'

    def parse_sales(self,gn,cat):
        page = 1
        html = self.session.get(self.url.format(gn,cat,page)).text
        soup = BeautifulSoup(html, 'lxml')
        prs = soup.find_all('div', attrs={'class': 'product-container'})
        goods = []
        refs = []
        while len(prs) > 0:
            for el in prs:
                data = el.find('a', attrs={'class': 'product-image'})
                href = data['href']
                id = href.split('/')[4]
                goods.append(id)
                refs.append(href)
            print(page,len(goods))
            time.sleep(1)
            page += 1
            html = self.session.get(self.url.format(gn,cat,page)).text
            soup = BeautifulSoup(html, 'lxml')
            prs = soup.find_all('div', attrs={'class': 'product-container'})

        data = pd.DataFrame({'good_id':goods,'ref':refs})
        data['good_id'] = data['good_id']#.astype('int64')
        return data

    def get_data(self):
        data = pd.DataFrame()
        for cat in CATS:
            for gn in SEX:
                print(cat,gn)
                data_rc= self.parse_sales(gn,cat)
                data_rc['sex'] = gn
                data_rc['cat'] = cat
                data = pd.concat([data,data_rc])
        data['sex'] = data['sex'].map(SEX_DICT)
        data['cat'] = data['cat'].map(CATS_DICT)
        data['cat'] = data['cat']#.astype('int64')
        return data


def main():
    parser = BrandParser()
    data = parser.get_data()
    data.to_csv('brand.csv',index=False)


if __name__ == "__main__":
    main()
