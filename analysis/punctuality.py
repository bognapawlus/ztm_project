import json
import os
import pandas as pd
import numpy as np
import folium
from datetime import datetime
import geopy
from unionfind import unionfind
import analysis.analysis_module


##CLASS TO ANALIZE DELAYS
class Punctuality:
    def __init__(self, locations_dict, schedule_dict):
        self.current_data = analysis.analysis_module.get_current_locations_object(
            locations_dict
        )
        self.schedule = analysis.analysis_module.get_schedule_object(schedule_dict)
        self.start_time = self.current_data.get_start_time_of_downloading()
        self.end_time = self.current_data.get_end_time_of_downloading()
        self.locations_folder = locations_dict
        self.schedule_folder = schedule_dict

        # dataFrame with busstops:
        self.all_busstop_data = self.schedule.get_busstops_data().copy()
        self.all_busstop_data["late"] = 0
        self.all_busstop_data["all"] = 0
        self.all_busstop_data_columns = self.all_busstop_data.columns

    def get_all_busstops(self):
        return self.all_busstop_data

    def get_locations_dir(self):
        return self.locations_folder

    def get_schedule_dir(self):
        return self.schedule_folder

    ##1. Counting late buses:
    def count_late_buses(self, how_many_counted_info):
        self.all_busstop_data = self.all_busstop_data.to_numpy()
        print(f"Total items to count: {len(self.all_busstop_data)}. How many counted:")

        i = 0
        ##opening schedule for each busstop and line
        for busstop_data in self.all_busstop_data:
            group_id = busstop_data[0]
            busstop_id = busstop_data[1]
            lat = float(busstop_data[3])
            lon = float(busstop_data[4])

            ##lines:
            lines = self.schedule.get_lines_from_busstop(
                group_id, busstop_id
            ).to_numpy()

            if len(lines) > 0 and len(lines[0][0]) >= 3:
                for line in lines:
                    current_schedule = self.schedule.get_schedule(
                        group_id, busstop_id, line[0], self.start_time, self.end_time
                    ).to_numpy()

                    for bus in current_schedule:
                        near_buses = len(
                            self.current_data.nearest_buses(
                                lat, lon, bus[1], 120, [line[0]], [bus[0]], 1
                            )
                        )
                        if near_buses == 0:
                            self.all_busstop_data[i][5] += 1
                        self.all_busstop_data[i][6] += 1
            i += 1

            if how_many_counted_info:
                if i % 10 == 0:
                    print(f"completed:{i}", end=", ")

        self.all_busstop_data = pd.DataFrame(
            self.all_busstop_data, columns=self.all_busstop_data_columns
        )
        print("Finished")

    def load_late_buses(self, file_name):
        self.all_busstop_data = pd.read_csv(file_name)

    def save_late_buses(self, file_name):
        self.all_busstop_data.to_csv(file_name)

    # 2. MAIN FUNCTION: Analysis of delay:
    def analize_delays(
        self, min_num_buses, min_delay_percent, biggest_delays_table, display_map
    ):
        df = self.all_busstop_data
        assert min_num_buses > 0
        bus_table = df.loc[df["all"] > min_num_buses].copy()  # delete trams
        bus_table["percent"] = bus_table["late"] / bus_table["all"]
        bus_table = bus_table.sort_values("percent", ascending=False)

        percent_of_delayed_buses = sum(bus_table["late"]) / sum(bus_table["all"]) * 100
        print(
            f"Buses were deleyed in {round(percent_of_delayed_buses, 2)}% measured cases."
        )

        busstops_without_delays = bus_table.loc[bus_table["percent"] == 0]
        print(f"Busstops without any delay: {len(busstops_without_delays)}")
        print(
            f"Number of busstops satisfing function's conditions (at least {min_num_buses} buses): {len(bus_table)}"
        )

        bus_table = bus_table.drop(columns=["Unnamed: 0"])

        if biggest_delays_table:
            print("Table with the most deleyed busstops:")
            display(bus_table.head(7))

        if display_map:
            print("Map with delays:")
            self.delays_map(
                bus_table[["szer_geo", "dlug_geo", "percent"]], min_delay_percent
            )
        self.delay_table = bus_table
        # return bus_table

    def get_delay_table(self):
        return self.delay_table

    def get_point_color(self, val):
        if val < 0.25:
            return "#2ecc71"
        elif val < 0.5:
            return "#f1c40f"
        elif val < 0.6:
            return "#f39c12"
        elif val < 0.8:
            return "#e67e22"
        elif val < 0.9:
            return "#d35400"
        else:
            return "#ba4a00"

    def delays_map(self, df, delay_percent):
        mapa = folium.Map([52.22, 21.01], zoom_start=12)
        np_coords = df.to_numpy()

        for el in np_coords:
            lat = el[0]
            lon = el[1]
            val = el[2]
            col = self.get_point_color(val)
            if val >= delay_percent:
                folium.CircleMarker(
                    [lat, lon],
                    radius=6,
                    fill_color=col,
                    fill=True,
                    color=False,
                    fill_opacity=1,
                    popup=str(val),
                ).add_to(mapa)

        display(mapa)

    # 3. Analysis of busstops with less delay rate for our object than for other object
    def get_better_busstops(self, punctuality_object2):
        tab1 = self.get_delay_table()
        tab2 = punctuality_object2.get_delay_table()

        df = pd.merge(tab1, tab2[["percent"]], left_index=True, right_index=True)
        df = df.loc[df["percent_x"] < df["percent_y"]]

        print(
            f'For "{self.get_locations_dir()}" there are {len(df)} busstops with better delay rate'
        )
        print(f'than for "{punctuality_object2.get_locations_dir()}"')

        new_data = df.copy()
        new_data["diff"] = new_data["percent_y"] - new_data["percent_x"]
        new_data = new_data.sort_values(by=["diff"], ascending=False)

        print("\nTable with the best difference busstops:")
        display(new_data[["slupek", "nazwa_zespolu", "diff"]].head(7))

        print("\nThe map shows busstops with smaller number of delays for our object")
        print("green point - small difference in delay rate")
        print("red point - big difference")
        self.delays_map(new_data[["szer_geo", "dlug_geo", "diff"]], 0)


def create_punctuality_object(locations_dict, schedule_dict):
    return Punctuality(locations_dict, schedule_dict)
