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