#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import ipaddress

import beaker.cache
import snmp_cmds
from beaker.cache import cache_region
from pysnmp.error import PySnmpError

from src.api.models import CdpNeighbor
from src.api.snmp.AbstractOperations import AbstractOperations
from src.api.snmp.SnmpUtils import SnmpUtils


class MiscOperations(AbstractOperations):

    def invalidate_cache(self):
        beaker.cache.region_invalidate(self.get_cdp_neighbors, 'api_data')
        beaker.cache.region_invalidate(self.get_hostname, 'api_data')
        beaker.cache.region_invalidate(self.get_uptime, 'api_data')

    def rebuild_cache(self):
        try:
            self.invalidate_cache()
            self.get_cdp_neighbors()
            self.get_hostname()
            self.get_uptime()
        except snmp_cmds.exceptions.SNMPTimeout as e:
            print('SNMPTimeout')
        # except error from pysnmp
        except PySnmpError as e:
            print('SNMPTimeout')
        except Exception as e:
            print(e)

    def __init__(self, ip, port, community, config):
        super().__init__(ip, port, community, config)

    # This needs to be cached
    @cache_region('api_data')
    def get_cdp_neighbors(self):
        """Return a list of cdp neighbors
        using those oids :
        cdp_neighbors:
            ip: 1.3.6.1.4.1.9.9.23.1.2.1.1.4.15
            fqdn: 1.3.6.1.4.1.9.9.23.1.2.1.1.6.15
            interface: 1.3.6.1.4.1.9.9.23.1.2.1.1.7.15
            model: 1.3.6.1.4.1.9.9.23.1.2.1.1.8.15
         """
        utils = SnmpUtils(self.ip, self.port, self.community)
        cdp_ips = list(utils.bulk(self.config['cdp_neighbors']['ip']).values())
        cdp_fqdns = list(utils.bulk(self.config['cdp_neighbors']['fqdn']).values())
        cdp_interfaces = list(utils.bulk(self.config['cdp_neighbors']['interface']).values())
        cdp_models = list(utils.bulk(self.config['cdp_neighbors']['model']).values())

        cdp_neighbors = []
        for i in range(len(cdp_ips)):
            try:
                cdp_neighbors.append(CdpNeighbor(
                    # convert ip from hex to human readable
                    ip=str(ipaddress.IPv4Address(int(cdp_ips[i], 16))),
                    fqdn=cdp_fqdns[i],
                    interface=cdp_interfaces[i],
                    model=cdp_models[i]
                ))
            except ValueError:
                cdp_neighbors.append(CdpNeighbor(
                    # convert ip from hex to human readable
                    ip="0.0.0.0",
                    fqdn=cdp_fqdns[i],
                    interface=cdp_interfaces[i],
                    model=cdp_models[i]
                ))
        return cdp_neighbors

    @cache_region('api_data')
    def get_hostname(self):
        """Return the hostname of the switch"""
        return snmp_cmds.snmpwalk(ipaddress=self.ip, port=self.port, community=self.community,
                                  oid=self.config['systemName'])[0][1]

    @cache_region('api_data')
    def get_uptime(self):
        """Return the uptime of the switch"""
        return snmp_cmds.snmpwalk(ipaddress=self.ip, port=self.port, community=self.community,
                                  oid=self.config['uptime'])[0][1]

    def set_hostname(self, hostname):
        """Set the hostname of the switch"""
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['systemName'], value=hostname, value_type='s')

