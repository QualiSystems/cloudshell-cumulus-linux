import re

from cloudshell.snmp.autoload.service.port_mapper import PortMappingService


class CumulusPortMappingService(PortMappingService):
    PORT_EXCLUDE_RE = re.compile(
        r"stack|engine|management|mgmt|null|voice|foreign|"
        r"cpu|control\s*ethernet\s*port|console\s*port|^br_.+|^vni-.+",
        re.IGNORECASE,
    )
