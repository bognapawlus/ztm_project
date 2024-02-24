import analysis.punctuality
import analysis.current_locations
import analysis.schedule

def get_current_locations_object(directory_name):
    return analysis.current_locations.create_current_locations_object(directory_name)

def get_punctuality_object(locations_dict, schedule_dict):
    return analysis.punctuality.create_punctuality_object(locations_dict, schedule_dict)

def get_schedule_object(directory_name):
    return analysis.schedule.get_object_with_schedule(directory_name)
