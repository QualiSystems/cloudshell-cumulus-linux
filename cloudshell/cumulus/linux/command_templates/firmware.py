from cloudshell.cli.command_template.command_template import CommandTemplate

from cloudshell.cumulus.linux.command_templates import ERROR_MAP

FIRMWARE_ERROR_MAP = {r"[Ff]ailure|[Ee]rror": "Failed to load firmware"}
FIRMWARE_ERROR_MAP.update(ERROR_MAP)


LOAD_FIRMWARE = CommandTemplate(
    "onie-install -fa -i {image_path}", error_map=FIRMWARE_ERROR_MAP
)
