#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from abc import abstractmethod
from threading import Thread

from beaker.cache import cache_regions, cache_region


class AbstractOperations:

    def __init__(self, ip, port, community, config):
        self.ip = ip
        self.port = port
        self.community = community
        self.config = config
        # defining beaker cache regions
        cache_regions.update(
            {
                'api_data': {
                    'type': 'memory',
                    'expire': 60 * 10,  # 10mn
                    'key_length': 250
                }
            }
        )

    def rebuild_cache_background(self):
        """Rebuild the beaker cache in background"""
        Thread(target=self.rebuild_cache).start()

    @abstractmethod
    def invalidate_cache(self):
        """Invalidate the beaker cache"""
        pass

    @abstractmethod
    def rebuild_cache(self):
        """Rebuild the beaker cache"""
        pass
