import pysnmp
from pysnmp import hlapi
def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value

def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result

def construct_value_pairs(list_of_pairs):
    pairs = []
    for key, value in list_of_pairs.items():
        pairs.append(pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(key), value))
    return pairs

def snmp_set(target, value_pairs, credentials, port=161, engine=pysnmp.hlapi.SnmpEngine(), context=pysnmp.hlapi.ContextData()):
    handler = pysnmp.hlapi.setCmd(
        engine,
        credentials,
        pysnmp.hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_value_pairs(value_pairs)
    )
    return fetch(handler, 1)[0]