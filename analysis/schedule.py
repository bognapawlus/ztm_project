import json
import os
import pandas as pd
import numpy as np
import folium
from datetime import datetime
import geopy
from unionfind import unionfind


##CLASS WITH SCHEDULE:
class Schedule:

    def __init__(self, directory_name):
        self.directory_schedule = directory_name
        file_name = "busstops.json"
        path = os.path.join(os.getcwd(), directory_name, file_name)

        with open(path) as f:
            json_data = json.load(f)

        bus_stops = json_data["result"]

        for i in range(len(bus_stops)):

            dicts = ["", "", "", "", "", ""]
            for index in 0, 1, 2, 4, 5:
                dicts[index] = {
                    value[index]["key"]: value[index]["value"]
                    for (key, value) in bus_stops[i].items()
                }

            bus_stops[i] = dicts[0] | dicts[1] | dicts[2] | dicts[4] | dicts[5]

        self.busstops_data = pd.DataFrame.from_dict(bus_stops)

    # 1. functions to get initial data
    def get_busstops_data(self):
        return self.busstops_data

    def get_lines_from_busstop(self, group_id, busstop_id):
        lines_file = f"{group_id}_{busstop_id}.json"
        path = os.path.join(os.getcwd(), self.directory_schedule, "lines", lines_file)

        with open(path) as f:
            json_data_onestop = json.load(f)

        list_of_lines = json_data_onestop["result"]
        if list_of_lines == []:
            return pd.DataFrame(columns=["linia"])
        else:
            for i in range(len(list_of_lines)):
                list_of_lines[i] = {
                    value[0]["key"]: value[0]["value"]
                    for (key, value) in list_of_lines[i].items()
                }

            return pd.DataFrame.from_dict(list_of_lines)

    def custom_to_datetime(self, date):
        # If the time is greater than 24, set it to 0
        int_time = int(date[11:13])
        if int_time >= 24:
            int_time = int_time - 24
            str_time = str(int_time)
            if int_time < 10:
                str_time = "0" + str_time

            return date[0:11] + str_time + date[13:]
        else:
            return date

    def get_schedule(
        self,
        group_id,
        busstop_num,
        line_num,
        downloading_start_time,
        downloading_end_time,
    ):
        schedule_file = f"schedule_{group_id}_{busstop_num}_{line_num}"
        path = os.path.join(
            os.getcwd(), self.directory_schedule, "schedule", schedule_file
        )

        with open(path) as f:
            json_data_oneline = json.load(f)

        list_a = json_data_oneline["result"]

        if list_a == []:
            ans = pd.DataFrame(columns=["brygada", "czas"])
            ans["czas"] = pd.to_datetime(ans["czas"])
            return ans
        else:
            for i in range(len(list_a)):
                dict0 = {
                    value[2]["key"]: value[2]["value"]
                    for (key, value) in list_a[i].items()
                }  # brigade
                dict1 = {
                    value[5]["key"]: self.directory_schedule[0:11] + value[5]["value"]
                    for (key, value) in list_a[i].items()
                }  # time
                list_a[i] = dict0 | dict1

            ##remove 24 hour:
            pd_table = pd.DataFrame.from_dict(list_a)
            pd_table["czas"] = pd_table["czas"].apply(self.custom_to_datetime)

            start_time = downloading_start_time + np.timedelta64(90, "s")
            end_time = downloading_end_time - np.timedelta64(90, "s")

            pd_table["czas"] = pd.to_datetime(pd_table["czas"])
            pd_table = pd_table.loc[pd_table["czas"] > start_time]
            pd_table = pd_table.loc[pd_table["czas"] < end_time]

            return pd_table


def get_object_with_schedule(directory_name):
    return Schedule(directory_name)
