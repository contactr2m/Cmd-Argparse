#!/usr/bin/env python
from argparse import ArgumentParser


# Non exiting argument parser.


class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent SystemExit in several occasions, as
    SystemExit is unacceptable when a command is called pragmatically.
    """

    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        super(CommandParser, self).__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (hasattr(self.cmd, 'missing_args_message') and not (args or any(not arg.startswith('-') for arg in args))):
            self.error(self.cmd.missing_args_message)
        return super(CommandParser, self).parse_args(args, namespace)

    def exit(self, status=0, message=None):
        raise ExitArgparse(status=status, message=message)

    def error(self, message):
        if self.cmd._called_from_command_line:
            super(CommandParser, self).error(message)
        else:
            raise CommandError("Error: %s" % message)
