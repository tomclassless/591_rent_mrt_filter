import json
from pathlib import Path
from typing import List

import pandas as pd
import requests as requests


class Station(object):
    def __init__(self, line_id, station_id, station_label, s_l_from_roadmap, station_name):
        self.line_id = line_id
        self.station_id = station_id
        self.station_label = station_label
        self.s_l_from_roadmap = s_l_from_roadmap
        self.station_name = station_name


class Line(object):
    def __init__(self, line_field, line_id, line_name):
        self.line_id = line_id
        self.line_field = line_field
        self.line_name = line_name
        self.stations: List[Station] = []


def parse_stations_from_api() -> List[Line]:
    session = requests.session()
    response = session.post('https://web.metro.taipei/apis/metrostationapi/menuline', {
        'LineID': "0",
        'Lang': 'tw'
    })
    lines_json = json.loads(response.text)
    lines: List[Line] = []
    for line_dict in lines_json:
        line = Line(
            line_id=line_dict.get('LineID'),
            line_field=line_dict.get('LineField'),
            line_name=line_dict.get('LineName'),
        )
        for station_dict in line_dict.get('LineStations'):
            station = Station(
                line_id=station_dict.get('LineID'),
                station_id=station_dict.get('SID'),
                station_label=station_dict.get('StationLabel'),
                s_l_from_roadmap=station_dict.get('StationLabelForRoadmap'),
                station_name=station_dict.get('StationName'),
            )
            line.stations.append(station)
        line.stations = sorted(line.stations, key=lambda x: x.station_id)
        lines.append(line)
    return lines


def get_route_info(start_sid: str, end_sid: str, session):
    response = session.post('https://web.metro.taipei/apis/metrostationapi/routetimepathinfo', {
        "StartSID": start_sid,
        "EndSID": end_sid,
        "Lang": "tw"})
    # {"StartSID":"088","EndSID":"007","StartStationName":"善導寺","EndStationName":"松山機場","TravelTime":"15",
    # "Path":"搭乘板南線（往南港展覽館）=> 忠孝復興站轉乘文湖線（往南港展覽館）","Lang":"tw"}
    return json.loads(response.text)


def get_distance_from_station(station_id='088', file_name='到善導寺時間'):
    lines = parse_stations_from_api()
    routes = []
    session = requests.session()
    for line in lines:
        for station in line.stations:
            if station.station_id != station_id:
                routes.append(get_route_info(station_id, station.station_id, session))
    routes = sorted(routes, key=lambda x: int(x.get('TravelTime')))
    final = [{
        'name': info.get('EndStationName'),
        'time': int(info.get('TravelTime'))
    } for info in routes]
    df = pd.DataFrame(final)
    df = df[~ (df.duplicated())]
    # Path("./mrt").mkdir(parents=True, exist_ok=True)
    # df.to_csv(f'./mrt/{file_name}.csv', index=False)
    return df
