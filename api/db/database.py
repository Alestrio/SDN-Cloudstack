#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import pymongo
import yaml


class Database:
    """
    Interface between the API and the MONGODB database
    """
    def __init__(self):
        try:
            with open('../../config/config.yaml') as file:
                config = yaml.load(file, Loader=yaml.Loader)['database']  # Opens database config
                connection_string = f"mongodb+srv://{config['username']}:{config['password']}@{config['host']}"
                self.client = pymongo.MongoClient(connection_string)
                self.database = self.client[config['database_name']]
                self.configs_collections = self.database['configs']
        except:
            print('No config file (ERRNO 101)')

    def get_configs(self):
        """
        Get the configs stored in database
        :return: List of configs
        """
        return self.configs_collections.find()

    def add_config(self, config: dict):
        """
        Adds a config to the database
        :param config: Dictionary of the configuration
        """
        self.configs_collections.insert_one(config)
