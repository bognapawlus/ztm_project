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
* **type2:** `YYYY-MM-DD schedule/busstops.json` - file with general busstops' data (mainly bustop coordinates)
* **type3:** `YYYY-MM-DD schedule/lines/gggg_ii.json` - file with all lines for busstop with group_id = gggg and number = ii
* **type4:** `YYYY-MM-DD schedule/schedule/schedule_gggg_ii_ll` - file with planned arrivals of bus nr ll on busstop gggg_ii

### Instruction of using

**functions:**



## Analysis module
The goal of this module is to create 3 objects:

* `current_locations object` - to analize type1 file e.g. counting too fast buses, describing localizations with 
frequently exceeded speed
* `schedule object` - generally used for create a table with busstops (from type2 file). It can also create DataFrames of type3 and type4 files
* `punctuality object` - it analizes current_locations and schedule object and displays statistics about delayed buses



### Instruction of using

**functions in module analysis.analysis_module:**
 
 * `get_current_locations_object(directory_name)` - returns current_locations object
 * `get_punctuality_object(locations_dict, schedule_dict):` - returns punctuality object
 * `get_schedule_object(directory_name)` - returns schedule object
 
 

**functions of current_locations object:**

* `analysis_of_all_buses_speed(speed_limit, display_map)` - analizes buses which exceeded the speed_limit. If display_map == True it shows a map with high speeds locations
* `get_locations_with_lots_overspeeds()` - analizes areas with at least 3 high speeds. It should be executing after analysis_of_all_buses_speed 

**functions of schedule object:**

* `get_busstops_data()` - returns pd.Dataframe table of type2 file
* `get_lines_from_busstop(group_id, busstop_id)` - returns pd.DataFrame table of type3 file
* `def get_schedule(group_id, busstop_num, line_num, downloading_start_time, downloading_end_time) - returns pd.DataFrame table of type4 file

**functions of punctuality object:**

* `get_all_busstops()` - returns table with busstops data (eg. coordinates, number of delayed buses for every busstop). It's dataFrame of type2 file
* `count_late_buses(how_many_counted_info)` - it counts columns **late**(delayed buses) and **all**(all buses) in busstops_table. It may take long time, so if how_many_counted_info = True it prints number off currently counted data
* `save_late_buses(file_name)` - saves busstops_table to csv file (after executing count_late_buses)
* `load_late_buses(file_name)` - we can use it instead of count_late_buses, when we have busstop_table with **late** and **all* columns created before
* `analize_delays(min_num_buses, min_delay_percent, biggest_delays_table, display_map)` analizes delays for busstops with at least min_num_buses and min_delay_percent during the considered period of time. If biggest_delays_table = True it displays table with 7 the most delayed busstops. If display_map = True, it displays a map with delays
