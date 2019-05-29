
'''
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

from  configparser import ConfigParser

section_names = ['DEFAULT','SYSTEM']

class MLAConfiguration(object):

    def __init__(self, *file_names):
        parser = ConfigParser()
        parser.optionxform = str  # make option names case sensitive
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')
        for name in section_names:
            print(type(name))
            self.__dict__.update(parser.items(name)) 


config = MLAConfiguration('config.cfg' )