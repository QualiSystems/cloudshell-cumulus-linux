from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cumulus.linux.command_templates import ERROR_MAP

# todo: move to SystemActions
SHUTDOWN = CommandTemplate("shutdown -h now", error_map=ERROR_MAP)
