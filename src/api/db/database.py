#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import json

import pymongo
import yaml
from bson import ObjectId


class Database:
    """
    Interface between the API and the MONGODB database
    """
    def __init__(self, config):
        connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}"
        self.client = pymongo.MongoClient(connection_string)
        self.database = self.client[config['database_name']]
        self.configs_collections = self.database['configs']

    def get_configs(self):
        """
        Get the configs stored in database
        :return: List of configs
        """
        configs = []
        for config in self.configs_collections.find({}):
            config['_id'] = str(config['_id']).replace('ObjectId(', '').replace(')', '')
            configs.append(config)
        return configs

    def add_config(self, config: dict):
        """
        Adds a config to the database
        :param config: Dictionary of the configuration
        """
        self.configs_collections.insert_one(config)

    def get_config(self, name):
        """
        Get a config from the database
        :param name: name of the config
        :return: Config
        """
        return self.configs_collections.find_one({'name': name})

    def delete_config(self, config_name):
        """
        Delete a config from the database
        :param config_name: Id of the config
        """
        self.configs_collections.delete_one({'name': config_name})

    def get_brief_configs(self):
        """
        Get the configs stored in database
        :return: List of configs
        """
        configs_names = []
        for config in self.configs_collections.find({}):
            config['_id'] = str(config['_id']).replace('ObjectId(', '').replace(')', '')
            configs_names.append(config['name'])
        return configs_names
