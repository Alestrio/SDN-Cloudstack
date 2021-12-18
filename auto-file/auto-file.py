import yaml


def create_config_file(**kwargs):
    """
    Format :
    database:
     host: cloudstack.chalons.univ-reims.fr
     port: 27017
     username: root
     password: iutchalons
     database_name: sdn-cloudstack
    api:
     route_prefix: /api/v1.5
    snmp:
     host: 10.59.10.64
     port: 161
     community: public
     name: Foo"""
    config = {'name': kwargs['name'],
              'database': {'host': kwargs['db_host'],
                           'port': kwargs['db_port'],
                           'username': kwargs['db_username'],
                           'password': kwargs['db_password'],
                           'database_name': kwargs['database_name']},
              'api': {'route_prefix': kwargs['api_route_prefix']},
              'snmp': {'host': kwargs['snmp_host'],
                       'port': kwargs['snmp_port'],
                       'community': kwargs['snmp_community']}}

    with open(f"{kwargs['name'].lower()}.yaml", 'w') as files:
        yaml.dump(config, files, default_flow_style=False)
        print(f"config files at : {kwargs['name'].lower()}.yaml, as been created.")


def create_proxy_files(**kwargs):
    with open('default_proxy.txt', 'r') as files:
        conf_proxy = files.read()
        proxy = conf_proxy.replace("{path}", f"{kwargs['name'].lower()}.{kwargs['domain_name']}").replace("{name}", kwargs['name'].lower())
        with open(f"proxy_{kwargs['name'].lower()}", 'w') as proxy_file:
            proxy_file.write(proxy)
            print(f"proxy files at : proxy_{kwargs['name'].lower()}, as been created.")

def get_data():
    config_dic = {'db_host': input("Data-Base host : "),
                  'db_port': int(input("Data-Base port : ")),
                  'db_username': input("Data-Base username : "),
                  'db_password': input("Data-Base password : "),
                  'database_name': input("Data-Base name : "),
                  'api_route_prefix': input("Api-Route prefix : "),
                  'snmp_host': input("SNMP host IP address : "),
                  'snmp_port': int(input("SNMP port : ")),
                  'snmp_community': input("SNMP community type : "),
                  'name': input("Name : "),
                  'domain_name': input("Domain name : ")}
    return config_dic

if __name__ == "__main__":
    config_dic = {'db_host': 'cloudstack.chalons.univ-reims.fr',
                  'db_port': 27017,
                  'db_username': 'root',
                  'db_password': 'iutchalons',
                  'database_name': 'sdn_cloudstack',
                  'api_route_prefix': '/api/v1.5',
                  'snmp_host': '10.59.10.64',
                  'snmp_port': 161,
                  'snmp_community': 'public',
                  'name': 'Foo',
                  'domain_name': 'sdn.chalons.univ-reims.fr'}

    # dic = get_data()
    create_config_file(**config_dic)
    create_proxy_files(**config_dic)
