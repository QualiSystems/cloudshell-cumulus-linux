from cloudshell.cli.session.session_exceptions import CommandExecutionException


class CumulusCommandError(CommandExecutionException):
    ...


class CommandNotFound(CumulusCommandError):
    def __init__(self):
        super().__init__("Command not found")


class CommandError(CumulusCommandError):
    def __init__(self):
        super().__init__("Command error")


class NotSupports2VlanAwareBridges(CumulusCommandError):
    def __init__(self):
        msg = "This version of Cumulus doesn't support 2 VLAN aware bridges"
        super().__init__(msg)


ERROR_MAP = {
    r"[Cc]ommand not found": CommandNotFound(),
    r"[Ee]rror:|ERROR:": CommandError(),
}
