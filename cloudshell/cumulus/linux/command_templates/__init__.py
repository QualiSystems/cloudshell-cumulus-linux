from cloudshell.cli.session.session_exceptions import CommandExecutionException


class CommandNotFound(CommandExecutionException):
    def __init__(self):
        super().__init__("Command not found")


class CommandError(CommandExecutionException):
    def __init__(self):
        super().__init__("Command error")


ERROR_MAP = {
    r"[Cc]ommand not found": CommandNotFound(),
    r"[Ee]rror:|ERROR:": CommandError(),
}
