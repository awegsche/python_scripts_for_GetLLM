

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
        return ",".join(aliases) + "\n" + self.help

class ATerm:
    def __init__(self):
        self.commands = []

    def add_command(self, aliases, action, thehelp=""):
        self.commands.append(ACommand(aliases, action, thehelp))

    def run_command(self, command):
        words = command.split(" ", 1)
        for cmd in self.commands:
            if words[0] in cmd.command_aliases:
                if len(words) > 1:
                    cmd.action(words[1])
                else:
                    cmd.action("")
                return True
        if command == 'help':
            for cmd in self.commands:
                print cmd.print_help()
                return True
        # if no command was executed, return False
        return False
