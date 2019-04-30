from collections import OrderedDict


ERROR_MAP = OrderedDict([(r'[Cc]ommand not found', 'Command not found'), (r'[Ee]rror:|ERROR:', 'Command error')])
