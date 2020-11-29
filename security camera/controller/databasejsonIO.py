import json

#reads the json file from database dump
#returns a python dictionary
def read_json(filepath):
    with open(filepath) as file:
        data_dictionary = json.loads(file)
        return data_dictionary

#takes a python dictionary and 
#converts it to a json file
def write_json(python_dict, filename):
    with open(filename, 'w') as json_file:
        json.dump(python_dict, json_file)

