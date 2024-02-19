from datetime import datetime
import time
import requests
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("end_time", help="file to be read")
args = parser.parse_args()

#1. time conversion:
# -- current_time -> time, when we start downoloading
# -- end_time -> time when we stop downolading
# -- number_of_items -> how many times downloading will be reapeted
now1 = datetime.now()
current_time = now1.strftime("%Y/%m/%d, %H:%M")
#wczytane = "23:05"
wczytane = args.end_time
end_time = datetime.now().strftime("%Y/%m/%d,") + " " + wczytane

d1 = datetime.strptime(current_time, "%Y/%m/%d, %H:%M")
d2 = datetime.strptime(end_time, "%Y/%m/%d, %H:%M")
x = d2 - d1
number_of_times = int(x.seconds/60)
number_of_times


#2. function to creating a directory with current date
def create_a_dict():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d, %H:%M")
    dict_name = current_time + " ztm"
    if not os.path.exists(dict_name):
        os.mkdir(dict_name)
        return dict_name
    else:
        print("error, we have that data downloaded")

def create_info_dict():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d schedule")
    dict_name = current_time
    if not os.path.exists(dict_name):
        os.mkdir(dict_name)
        return dict_name
    else:
        print("error, we have schedule downloaded") 
        
#data_dictionary = create_a_dict()

#3. function to download the single data with buses positions
def download_single_data(nr, data_id, dir_name):
    if data_id == 1: ##download current buses' localizations
        response = requests.post('https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=%20f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3&type=1')
        ans = response.text
        json_object = json.loads(ans)
        #if not os.path.exists(dir_name):
        #       os.mkdir(dir_name)
        path_f = os.path.join(os.getcwd(), dir_name, str(nr) + ".json")
        
        with open(path_f, "w") as file:
            json.dump(json_object, file)

def download_busstop_coordinates(info_dir_name):
    response = requests.post('https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3')
    ans = response.text
    json_object = json.loads(ans)
    path_f = os.path.join(os.getcwd(), info_dir_name, "busstops.json")
        
    with open(path_f, "w") as file:
        json.dump(json_object, file) 
        

#4. function to download all data which we wanted            
def download_data():
    data_dictionary = ''
    for i in range(number_of_times):
        if i == 0:
            data_dictionary = create_a_dict()
        download_single_data(i, 1, data_dictionary)
    time.sleep(60)

download_data()
        
