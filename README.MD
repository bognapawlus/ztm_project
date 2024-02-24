# Main project

## General description

After cloning the repository, we may install the package `ztm_package` by
```sh
 $ pip install path_to_directory
```

Package consists two modules

* `download` - to download all required data
* `analysis` - to make all analysis

Below are descriptions of both modules:



## Download module:
Creates 4 types of files:

* **type1:** `YYYY-MM-DD, hh:mm ztm/n_YYYY-MM-DD, hh:mm:ss.json` - file with json object of locations and other indentifying data
for current driving buses
* **type2:** `YYYY-MM-DD schedule/busstops.json` - file with general busstops' data (mainly bus stop coordinates)
* **type3:** `YYYY-MM-DD schedule/lines/gggg_ii.json` - file with all lines for busstop with group_id = gggg and number = ii
* **type4:** `YYYY-MM-DD schedule/schedule/schedule_gggg_ii_ll` - file with planned arrivals of bus nr ll on bus stop gggg_ii

### Instruction of using

**functions:**
* `download_data(number_of_times, schedule, current_buses)` - it downloads data from a website. If schedule = True, function
starts with downloading type2 file. If current buses = True, then type1 file will be downloaded number_of_times times (about every 60 seconds).

We can also download data with using dm.py file
```sh
 $ python3 dm.py 62
```
downloads current buses coordination 62 times and
```sh
 $ python3 dm.py 62 -s
```
downloads schedule first, and then it downloads current buses coordination 62 times.

## Analysis module
The goal of this module is to create 3 objects:

* `current_locations object` - to analyze type1 file e.g. counting too fast buses, describing localizations with
frequently exceeded speed
* `schedule object` - generally used for creating a table with bus stops (from type2 file). It can also create DataFrames of type3 and type4 files
* `punctuality object` - it analyzes current_locations and schedule object and displays statistics about delayed buses



### Instruction of using

**functions in module analysis.analysis_module:**
 
 * `get_current_locations_object(directory_name)` - returns current_locations object
 * `get_punctuality_object(locations_dict, schedule_dict):` - returns punctuality object
 * `get_schedule_object(directory_name)` - returns schedule object
 
 

**functions of current_locations object:**

* `analysis_of_all_buses_speed(speed_limit, display_map)` - analyzes buses which exceeded the speed_limit. If display_map == True it shows a map with high speeds locations
* `get_locations_with_lots_overspeeds()` - analyzes areas with at least 3 high speeds. It should be executing after analysis_of_all_buses_speed

**functions of schedule object:**

* `get_busstops_data()` - returns pd.Dataframe table of type2 file
* `get_lines_from_busstop(group_id, busstop_id)` - returns pd.DataFrame table of type3 file
* `def get_schedule(group_id, busstop_num, line_num, downloading_start_time, downloading_end_time) - returns pd.DataFrame table of type4 file

**functions of punctuality object:**

* `get_all_busstops()` - returns table with busstops data (eg. coordinates, number of delayed buses for every busstop). It's dataFrame of type2 file
* `count_late_buses(how_many_counted_info)` - it counts columns **late** (delayed buses) and **all** (all buses) in busstops_table. It may take long time, so if how_many_counted_info = True it prints number off currently counted data
* `save_late_buses(file_name)` - saves busstops_table to csv file (after executing count_late_buses)
* `load_late_buses(file_name)` - we can use it instead of count_late_buses, when we have busstop_table with **late** and **all* columns created before
* `analize_delays(min_num_buses, min_delay_percent, biggest_delays_table, display_map)` analyzes delays for busstops with at least min_num_buses and min_delay_percent during the considered period of time. If biggest_delays_table = True it displays a table with 7 the most delayed busstops. If display_map = True, it displays a map with delays
* `get_better_busstops(punctuality_object2)` - it compares busstops from one period of time with other. In a result we get busstops with smaller delay rate for default object. Function may be executed after analize_delays function

## Description of files and folders:

* `final_presentation.ipynb` - presentation of all object functions
* `analysis` - folder with all modules for data analysis
* `download` - folder with download module
* `dm.py` - program to download data
* `2024-02-20 schedule`, `2024-02-20, 12:38 ztm`, `2024-02-20, 19:50 ztm` - data used for our analysis
* `out1.csv`, `out2.csv` - tables received from count_late_buses (for hours 12:38 and 19:50)
* `profiler.ipynb` - profiler analysis




