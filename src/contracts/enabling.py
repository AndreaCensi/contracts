
class Switches:
    disable_all = False

def disable_all():
    ''' Disables all contracts checks. '''
    Switches.disable_all = True
    
def enable_all():
    ''' Enables all contracts checks. '''
    Switches.disable_all = False

def all_disabled():
    ''' Returns true if all contracts checks are disabled. '''
    return Switches.disable_all
