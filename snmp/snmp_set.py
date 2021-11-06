import pysnmp
from pysnmp import hlapi


# https://pastebin.com/GBWUJa4U


def fetch(handler, count):
    # TODO documentation, seems to be code gathered on internet
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


""" This function can be reused for other PySNMP functions, like GetBulk. It simply loops
on the handler for as many times as we tell it (count variable). If it encounters any
error it stops and raises a RuntimeError, if no error is encountered it stores the data
in a list of dictionaries.

try ... except StopIteration construct is in case the user specifies a higher number
of objects than it actually has, the code stops and returns what it has so far.

In each get() operation we get multiple OIDs, thus each dictionary will have as a key
the OID and as value the value of that OID in the MIB. In case it requires multiple OIDs
in a single Get it returns a dictinonary with multiple keys.

Using list in case the user needs the same information many times on different instance.
Such as errors on different interfaces where instance = interface. 

fetch() relies on function called cast() which just converts the data as received from
PySNMP to integer, float, or string. """


def construct_value_pairs(list_of_pairs):
    pairs = []
    for key, value in list_of_pairs.items():
        pairs.append(pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(key), value))
    return pairs

""" This function returns a list, that we can expand by prepending a "*" as we did above
in the get() function """


def snmp_set(target, value_pairs, credentials, port=161, engine=pysnmp.hlapi.SnmpEngine(),
             context=pysnmp.hlapi.ContextData()):
    handler = pysnmp.hlapi.setCmd(
        engine,
        credentials,
        pysnmp.hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_value_pairs(value_pairs)
    )
    return fetch(handler, 1)[0]

# TODO : cleanup this ENTIRE file
# It's trying to kill an ant with a BOEING 777