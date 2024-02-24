from datetime import datetime
import time
import requests
import json
import os
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--schedule", action="store_true", help="download schedule, busstop and lines")
parser.add_argument("-c", "--current_buses", action="store_true", help="download current buses' coordinates")
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
        
        #zrób folder na  linie:
        path1 = os.path.join(os.getcwd(), dict_name, "lines")
        if not os.path.exists(path1):
            os.mkdir(path1)

        #zrób folder na rozkład:
        path1 = os.path.join(os.getcwd(), dict_name, "schedule")
        if not os.path.exists(path1):
            os.mkdir(path1)
    
        return dict_name
    else:
        print("error, we have schedule downloaded")
        return -1
        
#data_dictionary = create_a_dict()

#3. function to download the single data with buses positions
def download_single_data(nr, dir_name):
    print(f"Downloading data {nr} .................. ", end='')
    response = requests.post('https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=%20f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3&type=1')
    download_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    ans = response.text
    json_object = json.loads(ans)

    #check if data are valid
    error_trials = 0
    while sys.getsizeof(json_object["result"]) < 1000:
        time.sleep(5)
        response = requests.post('https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=%20f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3&type=1')
        download_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        ans = response.text
        json_object = json.loads(ans)
        error_trials += 1

        if error_trials == 500:
            print("\nThere is a  problem with data downoloading. Do yo want to continue?")
            decision = input("Y/N: ")
            if decision != "Y":
                print("Data download stopped")
                break

    #if not os.path.exists(dir_name):
    #       os.mkdir(dir_name)
    path_f = os.path.join(os.getcwd(), dir_name, str(nr) + "_" + str(download_time) + ".json")

    with open(path_f, "w") as file:
        json.dump(json_object, file)
    print(f"Finished. Time: {download_time}")


def download_busstop_coordinates():
    schedule_dictionary_name = create_info_dict()
    
    if schedule_dictionary_name != -1:
        response = requests.post('https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3')
        ans = response.text
        json_object = json.loads(ans)
        
        while sys.getsizeof(json_object["result"]) < 1000:
            print("There was an error while trying to download schedule. Do you still want to try?")
            decision = input("Y/N: ")
            if decision == "Y":
                response = requests.post('https://api.um.warszawa.pl/api/action/dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3')
                ans = response.text
                json_object = json.loads(ans)   
            else:
                break
                ##TODO: how to end whole program
        
        path_f = os.path.join(os.getcwd(), schedule_dictionary_name, "busstops.json")

        with open(path_f, "w") as file:
            json.dump(json_object, file) 
            
    return schedule_dictionary_name
        

###....
def download_lines_and_schedules(dict_name):

    path_f = os.path.join(os.getcwd(), dict_name, "busstops.json")
    with open(path_f) as file:
        data = json.load(file)
        num = len(data["result"])
    print(f"Total number of items to download: {num}")

    i = 0
    lines_link = ''

    for el in data["result"]:
        
        s1 = el["values"][0]["value"]
        s2 = el["values"][1]["value"]
        s3 = ''
        
        if i >= 4695:
            lines_link = f"https://api.um.warszawa.pl/api/action/dbtimetable_get?\
id=88cd555f-6f31-43ca-9de4-66c479ad5942&\
busstopId={s1}&busstopNr={s2}\
&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3"
            print(lines_link)
            response = requests.post(lines_link)
            ans = response.text
            json_object = json.loads(ans) #tu mam dodane linie
            print(json_object)

            #print(json_object["result"])
            for el2 in json_object["result"]:
                print(el2)
                #print(el2["values"][0]["value"])
                print(f"Trying {s1} {s2} {s3}")
                s3 = el2["values"][0]["value"]
           
                file_name = f"schedule_{s1}_{s2}_{s3}"
                path_f = os.path.join(os.getcwd(), dict_name, "schedule", file_name)

                schedule_link = f"https://api.um.warszawa.pl/api/action/dbtimetable_get?\
id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&\
busstopId={s1}&busstopNr={s2}&line={s3}\
&apikey=a0f68861-c45e-421e-8c4a-922f188a01a3"
                response = requests.post(schedule_link)
                ans = response.text
                json_object2 = json.loads(ans) #tu mam dodane godziny przyjazdu

                with open(path_f, "w") as file:
                    json.dump(json_object2, file)

            #x = input()

            #zapis do plików
            file_name = f"{s1}_{s2}.json"
            path_f = os.path.join(os.getcwd(), dict_name, "lines", file_name)
            with open(path_f, "w") as file:
                json.dump(json_object, file)

        i += 1
        print(f"{i}.Busstop: {s1}, nr: {s2} -- download  completed.\n")

##.....

    

#4. function to download all data which we wanted            
def download_data():
    if args.schedule:
        print("Downloading schedule")
        dict_name = download_busstop_coordinates()
        download_lines_and_schedules(dict_name)
    
    if args.current_buses:
        data_dictionary = ''
        for i in range(number_of_times):
            if i == 0:
                data_dictionary = create_a_dict()
            download_single_data(i, data_dictionary)
            time.sleep(60)


download_data()
        
