#!/usr/bin/env python
import cmd
import traceback

CoreCmd = cmd.Cmd


class Cmd(CoreCmd):
    """
    Customized subclass of Python cmd module.
    """

    empty_line_repeats_last_command = False

    EOF_exits_command_loop = True

    identchars = cmd.IDENTCHARS + "/-."

    last_command_failed = False

    def __init__(self, *args, **kwargs):
        CoreCmd.__init__(self, *args, **kwargs)

    def onecmd(self, line):
        """
        Wrap error handling around cmd.Cmd.onecmd().
        :param line:
        :return:
        """

        self.last_command_failed = False
        try:
            return cmd.Cmd.onecmd(self, line)
        except SystemExit:
            raise
        except ExitArgparse, e:
            if e.message is not None:
                print e.message
            self.last_command_failed = e.status != 0
            return False
        except CommandError, e:
            print e
        except:
            traceback.print_exc()

        self.last_command_failed = True
        return False

    def do_EOF(self, arg):
        """
        EOF
        :param arg:
        :return:
        """

        if self.EOF_exits_command_loop and self.prompt:
            print
        return self.EOF_exits_command_loop

    def do_exit(self, arg):
        """
        Exit
        :param arg:
        :return:
        """

        return True

    do_quit = do_exit

    def emptyline(self):
        """
        Empty line does nothing.
        """

        if self.empty_line_repeats_last_command:
            cmd.Cmd.emptyline(self)

    def help_help(self):
        """
        Type "help [topic]" for help on a command,
        or just "help" for a list of commands.
        """

        self.stdout.write(self.help_help.__doc__ + "\n")

    def default(self, line):
        raise CommandError('No such command: %s\n' % line)
