#!/usr/bin/env python
from argparse import ArgumentParser


class ExitArgparse(Exception):
    """Exit method from ArgumentParser."""

    def __init__(self, message=None, status=0):
        super(ExitArgparse, self).__init__()
        self.message = message
        self.status = status


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a command. If this exception is raised during the execution
    of a  command, it will be caught and turned into a nicely-printed error message to the appropriate output stream
    (i.e., stderr); as a result, raising this exception (with a sensible description of the error) is the preferred
    way to indicate that something has gone wrong in the execution of a command.
    """
    pass


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
