import os


# This short script generates the configuration file for Mobot with the inputted information
def generateConfiguration(newfile, Token):
    if os.path.exists('config.py') and newfile == True:
        print("Config File Exists")
    else:
        with open('config.py', 'w') as files:
            files.write('Token = \'' + Token + '\'\n')
