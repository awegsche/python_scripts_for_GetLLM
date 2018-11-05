def read_logfile(filepath, only_modules=None):
    messages = []
    with open(filepath) as log:
        for line in log:
            parts = line.split(" | ")
            if len(parts) == 3:
                thismessage = LogMessage(*parts)
            else:
                thismessage = LogMessage("REP", line)
            if only_modules is None or thismessage.Sender in only_modules:
                messages.append(thismessage)
    return messages


class LogMessage:
    def __init__(self, level, message, sender="Unknown"):
        self.Level = level.strip()
        self.Message = message.strip()
        self.Sender = sender.strip()

