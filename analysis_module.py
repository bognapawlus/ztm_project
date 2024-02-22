import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium 
from datetime import datetime
import geopy 

class Current_locations:
    
    def __init__(self, directory_name):
        
        self.dict_name = directory_name
        self.list_of_files = os.listdir(os.path.join(os.getcwd(), directory_name))
        self.num_of_files = len(self.list_of_files)
        
        assert(self.num_of_files > 1)
        
        #create pandas data_frame for first file
        file_name = self.list_of_files[0]
        path = os.path.join(os.getcwd(), directory_name, file_name)
        f = open(path)
        json_data = json.load(f)
        self.data = pd.DataFrame.from_dict(json_data["result"])
        
        #create main pandas dataframe
        for i in range(1, self.num_of_files):
            self.__concatenate_data(i)
        self.data['Time'] = pd.to_datetime(self.data['Time'])

        
        #create list with all vehicle_numbers
        self.all_vehicle_numbers = self.data["VehicleNumber"].to_numpy()
        self.all_vehicle_numbers = np.unique(self.all_vehicle_numbers)
        
    def get_data(self):
        return self.data
    
    ##1. Functions for data preparation:
    def __concatenate_data(self, i):
        file_name = self.list_of_files[i]
        path = os.path.join(os.getcwd(), self.dict_name, file_name)
        f = open(path)
        json_data = json.load(f)
        data_i = pd.DataFrame.from_dict(json_data["result"])
        self.data = pd.concat([self.data, data_i], axis=0)
        
    def get_start_time_of_downloading(self):
        times = np.copy(self.list_of_files)
        for i in range(self.num_of_files):
            times[i] = times[i][:-5].split("_")[1].replace(',', '')
        times = times.astype("datetime64[ns]")
        return np.min(times)
    
    def get_end_time_of_downloading(self):
        times = np.copy(self.list_of_files)
        for i in range(self.num_of_files):
            times[i] = times[i][:-5].split("_")[1].replace(',', '')
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

    #https://pl.martech.zone/calculate-great-circle-distance/
    def __getDistanceBetweenPointsNew(self, latitude1, longitude1, latitude2, longitude2):

        theta = longitude1 - longitude2

        distance = 60 * 1.1515 * rad_to_deg(
            np.arccos(
                (np.sin(deg_to_rad(latitude1)) * np.sin(deg_to_rad(latitude2))) + 
                (np.cos(deg_to_rad(latitude1)) * np.cos(deg_to_rad(latitude2)) * np.cos(deg_to_rad(theta)))
            )
        )

        return round(distance * 1.609344, 2) #distance in kilometers
    
    ##3. Functions for calculating speed
    def __get_speed_list(self, np_single_bus_data, nrows, speed_limit):
        list_with_speeds = []
        coordinates_for_exceeded_speed = []
        
        for i in range(nrows - 1):
            if np_single_bus_data[i][3] < np_single_bus_data[i + 1][3]: #checking if times are different
                time = (np_single_bus_data[i + 1][3] - np_single_bus_data[i][3]).seconds
                lat1 = np_single_bus_data[i][4]
                lon1 = np_single_bus_data[i][1]
                lat2 = np_single_bus_data[i + 1][4]
                lon2 = np_single_bus_data[i + 1][1]
                if lat1 == lat2 and lon1 == lon2:
                    speed = 0
                else:
                    speed = getDistanceBetweenPointsNew(lat1, lon1, lat2, lon2) / (time / 3600) 
    
                list_with_speeds.append(round(speed, 2))
                if speed > speed_limit:
                    coords = [(lat1 + lat2) / 2, (lon1 + lon2) / 2]
                    coordinates_for_exceeded_speed.append(coords)
        
        return [list_with_speeds, coordinates_for_exceeded_speed]
    
    ##4. speed analysis for one bus
    def analysis_for_one_bus(self, bus_id, speed_limit):
        min_time = self.get_start_time_of_downloading() - np.timedelta64(60,'s')
        bus = self.data[self.data["VehicleNumber"] == bus_id]
        bus = bus.sort_values("Time")
        bus_good_time = bus[bus["Time"] > min_time]
        ##ans[np.bus_table, n_rows, speed_list, max_speed]
        ans = ['', '', '', '', '']
        ans[0] = bus_good_time.to_numpy() # table with coordinates for one bus
        ans[1] = len(bus_good_time.axes[0]) # computing number of rows
        ans[2] = [] # list with speeds of our bus in measured time
        ans[3] = 0 # maximum speed of bus
        ans[4] = [] # coordinates for exceeded speed
        
        if ans[1] <= 1:
            print(f"Not enough data. Can't anylise bus's {bus_id} locations.")
        else:
            ans[2] = self.__get_speed_list(ans[0], ans[1], speed_limit)[0]
            if len(ans[2]) > 0:
                ans[3] = np.max(ans[2])
            ans[4] = self.__get_speed_list(ans[0], ans[1], speed_limit)[1]
 
        return ans

    ##5. speed analysis for every buses
    def analysis_of_all_buses_speed(self, speed_limit):
        how_many_buses_exceeded_the_speed = 0
        self.places_with_exceeded_speed = pd.DataFrame(columns=['Lat', 'Lon'])
        
        for bus_id in self.all_vehicle_numbers:
            single_bus_analysis = self.analysis_for_one_bus(bus_id, speed_limit)
            if single_bus_analysis[1] > 1: #num_rows > 1
                print(f"id={bus_id}, maxs={single_bus_analysis[3]}")
                if single_bus_analysis[3] > speed_limit and single_bus_analysis[3] < 150:
                    how_many_buses_exceeded_the_speed += 1
                    self.__add_coords_to_speed_list(single_bus_analysis[4])
            else:
                print("empty table")
        
        print(how_many_buses_exceeded_the_speed)
        return [how_many_buses_exceeded_the_speed, self.places_with_exceeded_speed]
        
        
    def __add_coords_to_speed_list(self, new_coordinates):
        self.places_with_exceeded_speed = pd.concat([self.places_with_exceeded_speed, 
                                                     pd.DataFrame(new_coordinates).rename(columns={0: "Lat", 1: "Lon"})], axis=0)
        
    ##6. Functions for getting nearest buses
    def __time_dist(self, time1, time2):
        if time1 > time2:
            return (time1 - time2).seconds
        else:
            return (time2 - time1).seconds    
        
    def nearest_buses(self, lat0, lon0, time, dist_of_time, lines_list, dist_km): 
        data = self.data.loc[self.data["Time"].apply(lambda x : self.__time_dist(x, time)) < dist_of_time]
        data = data.loc[data["Lines"].isin(lines_list)]
        return data.loc[getDistanceBetweenPointsNew(lat0, lon0, data["Lat"], data["Lon"]) < dist_km] 
    
    

def analize_current_buses_locations(directory_name):
    return Current_locations(directory_name)
