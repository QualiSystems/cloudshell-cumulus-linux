from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cumulus.linux.command_templates import ERROR_MAP


COMMIT = CommandTemplate('net commit', error_map=ERROR_MAP)

ABORT = CommandTemplate('net abort', error_map=ERROR_MAP)
