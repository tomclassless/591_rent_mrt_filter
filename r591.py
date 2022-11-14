import datetime
import json
from pathlib import Path
from pprint import pprint

import pandas
import requests
from bs4 import BeautifulSoup


class Crawler591(object):

    def __init__(self):
        self.header = {
            'user-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
        }
        self.session = requests.Session()
        res = self.session.get('https://rent.591.com.tw/?kind=1&region=1&section=5', headers=self.header)
        soup = BeautifulSoup(res.text, 'lxml')
        token = soup.select_one('meta[name="csrf-token"]')['content']
        self.header['X-CSRF-TOKEN'] = token

    @staticmethod
    def _default_search_condition():
        return {
            'is_format_data': 1,
            'is_new_list': 1,
            'type': 1,
            'region': 3,
            'showMore': 1,
            'multiNotice': 'boy,all_sex',
            'option': 'broadband,bed,washer,cold',
            'other': 'near_subway',
            'order': 'posttime',
            'orderType': 'desc',
        }

    def get_house_list(self, region: int, kind: int, price_low: int, price_high: int):
        page_start = 0
        total_items = 30
        data = []
        while page_start < total_items:
            params = self._default_search_condition()
            params.update(
                {'firstRow': page_start,
                 'region': region,
                 'kind': kind,
                 'rentprice': f'{price_low},{price_high}'}
            )
            self.session.cookies.set('urlJumpIp', str(region), domain='.591.com.tw')
            res = self.session.get(url='https://rent.591.com.tw/home/search/rsList', headers=self.header, params=params)
            response = json.loads(res.text)
            data.extend(response.get('data').get('data'))
            total_items = int(response.get('records'))
            page_start += 30
        for room in data:
            room.update(room.get('surrounding'))
            room.pop('surrounding')

        df = pandas.DataFrame(data)
        df['station'] = df['desc'].str.slice(start=1)
        return df


def save_591_csv(price_low: int, price_high: int):
    df = pandas.concat([(Crawler591().get_house_list(region=1, kind=3, price_low=price_low, price_high=price_high)),
                        (Crawler591().get_house_list(region=3, kind=3, price_low=price_low, price_high=price_high)),
                        (Crawler591().get_house_list(region=1, kind=2, price_low=price_low, price_high=price_high)),
                        (Crawler591().get_house_list(region=3, kind=2, price_low=price_low, price_high=price_high)),
                        (Crawler591().get_house_list(region=1, kind=1, price_low=price_low, price_high=price_high)),
                        (Crawler591().get_house_list(region=3, kind=1, price_low=price_low, price_high=price_high))
                        ])

    df['station'] = df['station'].fillna('站')
    df['station'] = df['station'].apply(lambda x: f'{x}站' if not x.endswith('站') else x)
    df['station'] = df['station'].apply(lambda x: x[2:] if x.startswith('捷運') else x)
    df['station'] = df['station'].apply(lambda x: '台北車站' if x == '台北車站站' else x)
    df['distance'] = df['distance'].fillna('0公尺')
    df['distance'] = df['distance'].apply(lambda x: int(x[:-2]))

    df.to_csv('591/all.csv', index=False)

    Path("./591").mkdir(parents=True, exist_ok=True)
    df = df[['title', 'post_id', 'kind_name', 'floor_str', 'price', 'section_name', 'role_name', 'area', 'contact', 'refresh_time', 'station',
             'distance']]
    return df
