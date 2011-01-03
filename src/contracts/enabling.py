
class Switches:
    disable_all = False

def disable_all():
    Switches.disable_all = True
    
def enable_all():
    Switches.disable_all = False

def all_disabled():
    return Switches.disable_all
