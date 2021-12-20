#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

#Load yaml config file
import yaml
import os

config_dir = os.getenv('CONFIG_DIR')

file = open(f'{config_dir}/config.yaml')
config = yaml.load(file, Loader=yaml.Loader)

listening_address = config['listening_address']
