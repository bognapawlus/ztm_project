import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium 
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
    
    def get_all_vehicle_numbers(self):
        return self.all_vehicle_numbers
    
    ##2. 
    def analysis_for_one_bus(self, bus_id):
        min_time = self.get_start_time_of_downloading() - np.timedelta64(60,'s')
        bus = self.data[self.data["VehicleNumber"] == bus_id]
        bus = bus.sort_values("Time")
        bus_good_time = bus[bus["Time"] > min_time]
        ##ans[bus_table, n_rows, ]
        ans = ['', '', '']
        return bus_good_time.to_numpy()

