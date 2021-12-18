#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

#Load yaml config file
import yaml
import os

with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r') as ymlfile:
    cfg = yaml.load(ymlfile, ymlfile)

listening_address = cfg['listening_address']
