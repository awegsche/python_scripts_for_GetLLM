

class ACommand:
    def __init__(self):
        self.command_aliases = []
        self.action = None
        self.help = ""

    def __init__(self, aliases, action, thehelp):
        self.command_aliases = aliases
        self.action = action
        self.help = thehelp

    def print_help(self):
        helpstring = self.help
        if self.action.__doc__:
            helpstring = self.action.__doc__
        return ("\n\n" + "- " * 50 + "\n\n"
                "      \33[1m" + ", ".join(self.command_aliases) + "\33[21m\n\n" + helpstring)

class ATerm:
    """The python terminal. This class contains several actions. An action is a function that takes
    a string as arguments. This string can either be empty or further specifying the command."""

    def __init__(self):
        self.commands = []

    def add_command(self, aliases, action, thehelp=""):
        self.commands.append(ACommand(aliases, action, thehelp))

    def run_command(self, command):
        try:
            words = command.split(" ", 1)
            for cmd in self.commands:
                if words[0] in cmd.command_aliases:
                    if len(words) > 1:
                        cmd.action(words[1])
                    else:
                        cmd.action("")
                    return True
            if words[0] == 'help':
                for cmd in self.commands:
                    if len(words) == 1:
                        print cmd.print_help()
                    elif words[1] in cmd.command_aliases:
                        print cmd.print_help()
                return True
            # if no command was executed, return False
            return False
        except KeyboardInterrupt:
            print "-+-+-+-+-+-+-+  interrupt -+-+-+-+-+-+-+-+-+"
            return True

