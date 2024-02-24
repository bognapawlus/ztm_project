import json
import os
import pandas as pd
import numpy as np
import folium
from datetime import datetime
import geopy
from unionfind import unionfind


class Current_locations:

    def __init__(self, directory_name):

        self.dict_name = directory_name
        self.list_of_files = os.listdir(os.path.join(os.getcwd(), directory_name))
        self.num_of_files = len(self.list_of_files)

        assert self.num_of_files > 1

        # create pandas data_frame for first file
        file_name = self.list_of_files[0]
        path = os.path.join(os.getcwd(), directory_name, file_name)
        with open(path) as f:
            json_data = json.load(f)
        self.data = pd.DataFrame.from_dict(json_data["result"])

        # create main pandas dataframe
        for i in range(1, self.num_of_files):
            self.__concatenate_data(i)
        self.data["Time"] = pd.to_datetime(self.data["Time"])

        # create list with all vehicle_numbers
        self.all_vehicle_numbers = self.data["VehicleNumber"].to_numpy()
        self.all_vehicle_numbers = np.unique(self.all_vehicle_numbers)

    def get_data(self):
        return self.data

    ##1. Functions for data preparation:
    def __concatenate_data(self, i):
        file_name = self.list_of_files[i]
        path = os.path.join(os.getcwd(), self.dict_name, file_name)
        with open(path) as f:
            json_data = json.load(f)
        data_i = pd.DataFrame.from_dict(json_data["result"])
        self.data = pd.concat([self.data, data_i], axis=0)

    def get_start_time_of_downloading(self):
        times = np.copy(self.list_of_files)
        for i in range(self.num_of_files):
            times[i] = times[i][:-5].split("_")[1].replace(",", "")
        times = times.astype("datetime64[ns]")
        return np.min(times)

    def get_end_time_of_downloading(self):
        times = np.copy(self.list_of_files)
        for i in range(self.num_of_files):
            times[i] = times[i][:-5].split("_")[1].replace(",", "")
        times = times.astype("datetime64[ns]")
        return np.max(times)

    def get_all_vehicle_numbers(self):
        return self.all_vehicle_numbers

    ##2. Functions for calulating distance
    def __rad_to_deg(self, radians):
        degrees = radians * 180 / np.pi
        return degrees

    def __deg_to_rad(self, degrees):
        radians = degrees * np.pi / 180
        return radians

    # formula from https://pl.martech.zone/calculate-great-circle-distance/
    def __getDistanceBetweenPointsNew(
        self, latitude1, longitude1, latitude2, longitude2
    ):

        if latitude1 == latitude2 and longitude1 == longitude2:
            return round(0, 2)

        theta = longitude1 - longitude2

        distance = (
            60
            * 1.1515
            * self.__rad_to_deg(
                np.arccos(
                    (
                        np.sin(self.__deg_to_rad(latitude1))
                        * np.sin(self.__deg_to_rad(latitude2))
                    )
                    + (
                        np.cos(self.__deg_to_rad(latitude1))
                        * np.cos(self.__deg_to_rad(latitude2))
                        * np.cos(self.__deg_to_rad(theta))
                    )
                )
            )
        )

        return round(distance * 1.609344, 2)  # distance in kilometers

    ##3. Functions for calculating speed
    def __get_speed_list(self, np_single_bus_data, nrows, speed_limit):
        list_with_speeds = []
        coordinates_for_exceeded_speed = []

        for i in range(nrows - 1):
            if (
                np_single_bus_data[i][3] < np_single_bus_data[i + 1][3]
            ):  # checking if times are different
                time = (np_single_bus_data[i + 1][3] - np_single_bus_data[i][3]).seconds
                lat1 = np_single_bus_data[i][4]
                lon1 = np_single_bus_data[i][1]
                lat2 = np_single_bus_data[i + 1][4]
                lon2 = np_single_bus_data[i + 1][1]
                if lat1 == lat2 and lon1 == lon2:
                    speed = 0
                else:
                    speed = self.__getDistanceBetweenPointsNew(
                        lat1, lon1, lat2, lon2
                    ) / (time / 3600)

                list_with_speeds.append(round(speed, 2))
                if speed > speed_limit:
                    coords = [(lat1 + lat2) / 2, (lon1 + lon2) / 2]
                    coordinates_for_exceeded_speed.append(coords)

        return [list_with_speeds, coordinates_for_exceeded_speed]

    ##4. speed analysis for one bus
    def analysis_for_one_bus(self, bus_id, speed_limit):
        min_time = self.get_start_time_of_downloading() - np.timedelta64(60, "s")
        bus = self.data[self.data["VehicleNumber"] == bus_id]
        bus = bus.sort_values("Time")
        bus_good_time = bus[bus["Time"] > min_time]
        ##ans[np.bus_table, n_rows, speed_list, max_speed, coordinates]
        ans = ["", "", "", "", ""]
        ans[0] = bus_good_time.to_numpy()  # table with coordinates for one bus
        ans[1] = len(bus_good_time.axes[0])  # computing number of rows
        ans[2] = []  # list with speeds of our bus in measured time
        ans[3] = 0  # maximum speed of bus
        ans[4] = []  # coordinates for exceeded speed

        if ans[1] <= 1:
            pass
            # print(f"Not enough data. Can't anylise bus's {bus_id} locations.")
        else:
            ans[2] = self.__get_speed_list(ans[0], ans[1], speed_limit)[0]
            if len(ans[2]) > 0:
                ans[3] = np.max(ans[2])
            ans[4] = self.__get_speed_list(ans[0], ans[1], speed_limit)[1]

        return ans

    ##5. speed analysis for every buses
    def display_map_with_points(self, df):
        mapa = folium.Map([52.22, 21.01], zoom_start=12)
        np_coords = df.to_numpy()

        for el in np_coords:
            lat = el[0].item()
            lon = el[1].item()
            folium.Marker([lat, lon], popup="over 60").add_to(mapa)

        display(mapa)

    # ONE OF MAIN FUNCTIONS: it counts speeding and displays map with speeding location
    def analysis_of_all_buses_speed(self, speed_limit, display_map):
        how_many_buses_exceeded_the_speed = 0
        self.places_with_exceeded_speed = pd.DataFrame(columns=["Lat", "Lon"])

        for bus_id in self.all_vehicle_numbers:
            single_bus_analysis = self.analysis_for_one_bus(bus_id, speed_limit)
            if single_bus_analysis[1] > 1:  # num_rows > 1
                # print(f"id={bus_id}, maxs={single_bus_analysis[3]}")
                if (
                    single_bus_analysis[3] > speed_limit
                    and single_bus_analysis[3] < 150
                ):
                    how_many_buses_exceeded_the_speed += 1
                    self.__add_coords_to_speed_list(single_bus_analysis[4])
            # else:
            # print("empty table")

        print(f"How many buses exceeded the speed: {how_many_buses_exceeded_the_speed}")

        if display_map:
            self.display_map_with_points(self.places_with_exceeded_speed)

        return [how_many_buses_exceeded_the_speed, self.places_with_exceeded_speed]

    # function for table with speedings locations -
    # it puts locations into one group when a location is near to the other one in the group
    def __create_grouped_places_with_exceeded_speed(self):
        df_np = self.places_with_exceeded_speed.to_numpy()
        num_buses = len(df_np)
        distance_array = np.zeros((num_buses, num_buses))

        u = unionfind(num_buses)

        for i in range(num_buses):
            for j in range(num_buses):
                # latitude1, longitude1, latitude2, longitude2
                if i != j:
                    distance_array[i][j] = self.__getDistanceBetweenPointsNew(
                        df_np[i][0], df_np[i][1], df_np[j][0], df_np[j][1]
                    )
                    if distance_array[i][j] <= 1:  # distance in kilometers
                        u.unite(i, j)

        self.dist_array = distance_array
        self.group_places = u.groups()

    ##sort list with locations to draw a line
    def __sorted_list(self, list_of_locations):
        df_np = self.places_with_exceeded_speed.to_numpy()
        n = len(list_of_locations)
        list_cp = list_of_locations.copy()
        for r in range(n - 1):
            for i in range(n - 1):
                if df_np[list_cp[i]][1] > df_np[list_cp[i + 1]][1]:
                    list_cp[i], list_cp[i + 1] = list_cp[i + 1], list_cp[i]

        return list_cp

    def get_locations_with_lots_overspeeds(self):
        self.__create_grouped_places_with_exceeded_speed()
        df_np = self.places_with_exceeded_speed.to_numpy()
        lots_of_overspeeds = [gr for gr in self.group_places if len(gr) > 2]
        print(
            f"There were {len(lots_of_overspeeds)} areas where at least 3 buses exceded the speed limit."
        )
        print(
            f"Map with these places with aproximate high-speed-steets and with informations \n\
        how many high-speed measurements where in this area:"
        )
        m = folium.Map([52.22, 21.01], zoom_start=11)
        list_of_colors = [
            "#2ecc71",
            "#d35400",
            "#af7ac5",
            "#5dade2",
            "#f4d03f",
            "#7e5109",
            "#f39c12",
        ]
        col_nr = 0

        for el in lots_of_overspeeds:
            list_map = self.__sorted_list(el)
            list_n = len(list_map)
            # print(list_map)

            for i in range(list_n - 1):
                # draw a line from i to i + 1:
                folium.PolyLine(
                    [df_np[list_map[i]], df_np[list_map[i + 1]]],
                    color=list_of_colors[col_nr],
                ).add_to(m)

            folium.CircleMarker(
                df_np[list_map[int((list_n - 1) / 2)]],
                radius=20,
                fill_color=list_of_colors[col_nr],
                fill=True,
                color=False,
                fill_opacity=0.6,
                popup=str(list_n),
            ).add_to(m)

            col_nr = (col_nr + 1) % 7

        display(m)

    def __add_coords_to_speed_list(self, new_coordinates):
        self.places_with_exceeded_speed = pd.concat(
            [
                self.places_with_exceeded_speed,
                pd.DataFrame(new_coordinates).rename(columns={0: "Lat", 1: "Lon"}),
            ],
            axis=0,
        )

    ##6. Functions for getting nearest buses
    def __time_dist(self, time1, time2):
        if time1 > time2:
            return (time1 - time2).seconds
        else:
            return (time2 - time1).seconds

    def nearest_buses(
        self, lat0, lon0, time, dist_of_time, lines_list, brigade_list, dist_km
    ):
        data = self.data.loc[
            self.data["Time"].apply(lambda x: self.__time_dist(x, time)) < dist_of_time
        ]
        data = data.loc[data["Lines"].isin(lines_list)]
        data = data.loc[data["Brigade"].isin(brigade_list)]
        return data.loc[
            self.__getDistanceBetweenPointsNew(lat0, lon0, data["Lat"], data["Lon"])
            < dist_km
        ]


def create_current_locations_object(directory_name):
    return Current_locations(directory_name)
