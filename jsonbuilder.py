import json
import os


# This short script generates the configuration file for Mobot with the inputted information
# Takes a dictionary and exports it to the configuration file
def exportConfiguration(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)


# Imports the json file and imports it into the program
def importConfiguration():
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r') as file:
            config = json.load(file)
    return config


def exportJson(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)


def importJson(filepath):
    data = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
    return data
