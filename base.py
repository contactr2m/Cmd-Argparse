#!/usr/bin/env python
from command_parser import CommandParser


class OutputWrapper(object):
    """
    Wrapper around stdout/stderr
    """

    def __init__(self, out, ending='\n'):
        self._out = out
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg, ending=None):
        ending = self.ending if ending is None else ending
        if type(msg) is not str:
            msg = str(msg)
        if ending and not msg.endswith(ending):
            msg += ending
        self._out.write(str(msg))


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a command. If this exception is raised during the execution
    of a  command, it will be caught and turned into a nicely-printed error message to the appropriate output stream
    (i.e., stderr); as a result, raising this exception (with a sensible description of the error) is the preferred
    way to indicate that something has gone wrong in the execution of a command.
    """
    pass


class SystemCheckError(CommandError):
    """
    The system check framework detected unrecoverable errors.
    """
    pass


class BaseCommand(object):
    """
    The base class from which all commands ultimately derive.

    1.  The ``run_from_argv()`` method calls ``create_parser()`` to get an ``ArgumentParser`` for the arguments, parses
        them and then calls the ``execute()`` method, passing parsed arguments.

    2.  The ``execute()`` method attempts to carry out the command by calling the ``handle()`` method with the parsed
        arguments; any output produced by ``handle()`` will be printed to standard output.

    3.  If ``handle()`` or ``execute()`` raised any exception (e.g. ``CommandError``), ``run_from_argv()`` will
        instead print an error message to ``stderr``.

    ``help``
        A short description of the command, which will be printed in help messages.
    """

    help = ''
    prog = ''
    # Configuration shortcuts that alter various logic.
    _called_from_command_line = False

    def __init__(self, stdout=None, stderr=None):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        self.prog = self.__class__.__name__ if self.prog is '' else self.prog
        self.parser = self.create_parser(subcommand=self.prog)
        self.last_command = self.prog

    def create_parser(self, subcommand, **kwargs):
        """
        Create and return the ``ArgumentParser`` which will be used to parse the arguments to this command.
        """

        parser = CommandParser(self, prog="%s" % subcommand, description=self.help or None, add_help=False, **kwargs)
        parser.add_argument('--traceback', action='store_true', help=SUPPRESS)

        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for sub_classed commands to add custom arguments.
        """
        pass

    def run_from_argv(self, argv):
        """
        If the command raises a ``CommandError``, intercept it and print it sensibly to stderr.
        If the ``--traceback`` option is present or the raised ``Exception`` is not ``CommandError``, raise it.
        """

        self._called_from_command_line = True

        options = self.parser.parse_args(argv)
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())

        try:

            self.execute(*args, **cmd_options)

        except CommandError as e:
            print e.message
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)
        finally:
            pass

    def execute(self, *args, **options):
        """
        Try to execute this command, performing system checks if needed (as controlled by the ``requires_system_checks``
         attribute, except if force-skipped).
        """

        if options.get('stdout'):
            self.stdout = OutputWrapper(options['stdout'])
        if options.get('stderr'):
            self.stderr = OutputWrapper(options['stderr'])

        try:
            output = self.handle(*args, **options)
            if output:
                self.stdout.write(output)
        finally:
            # You can do more processing here if required before returning the output.
            pass
        return output

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """

        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')
