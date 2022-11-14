import datetime
import time
import webbrowser

import pandas as pd
from pandas import DataFrame

from taipei_mrt import get_distance_from_station
from my_send_mail import sendmail
from r591 import save_591_csv


def near_stations():
    stations = get_distance_from_station()
    stations['name'] = stations['name'].apply(lambda x: f'{x}站' if not x.endswith('站') else x)
    return stations


def append(df: DataFrame, row: dict):
    new_row = pd.DataFrame(row, index=[0])
    df2 = pd.concat([new_row, df.loc[:]]).reset_index(drop=True)
    return df2


def check_591(mail=False, browser=False):
    print(str(datetime.datetime.now()), 'start check 591')

    rooms_591 = save_591_csv(price_low=9000, price_high=12000)
    rooms_591.to_csv('591/all.csv')
    near_station = near_stations()

    combined = pd.merge(left=near_station, right=rooms_591, left_on='name', right_on='station')
    combined.sort_values(by=['time'])
    combined = combined[~(combined['floor_str'].str.contains(pat='頂樓加蓋'))]
    combined = combined[~(combined['floor_str'].str.contains(pat='B'))]
    combined = combined[~(combined['role_name'].str.contains(pat='仲介'))]
    combined = combined[~(combined['role_name'].str.contains(pat='代理'))]
    combined = combined[combined['time'] <= 10]
    combined = combined[combined['distance'] <= 500]
    with open('591/list/black_list.txt', 'r') as blacklist_file:
        blacklist = [int(x) for x in blacklist_file.read().splitlines()]
    combined = combined[~(combined['post_id'].isin(blacklist))]

    seen_df = pd.read_csv('591/list/seen.csv')
    print(len(combined))
    for post_id in combined['post_id']:
        browser and webbrowser.open(f'https://rent.591.com.tw/home/{post_id}')
        seen_row = seen_df.loc[seen_df['post_id'] == post_id]
        if len(seen_row) == 0:
            message = 'this is new, '
            seen_df = append(seen_df, {'post_id': post_id, 'timestamp': time.time_ns(), 'exist': True})
            mail and sendmail(f'https://rent.591.com.tw/home/{post_id}')
        else:
            start = seen_row['timestamp'].tolist()[0]
            message = f'has seen for {int((time.time_ns() - start) / (86400 * 1e9))} days '

        print(f'{message}https://rent.591.com.tw/home/{post_id}')

    seen_df.loc[~(seen_df['post_id'].isin(combined['post_id'].tolist())), 'exist'] = False
    seen_df.to_csv('591/list/seen.csv', index=False)

    print(str(datetime.datetime.now()), 'end check 591')


if __name__ == '__main__':
    check_591(mail=False, browser=True)
