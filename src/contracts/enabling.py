from . import logger


class Switches:
    disable_all = False


def disable_all():
    ''' Disables all contracts checks. '''
    Switches.disable_all = True
    logger.info('All contracts checking disabled.')


def enable_all():
    ''' Enables all contracts checks. '''
    Switches.disable_all = False
    logger.info('All contracts checking enabled.')


def all_disabled():
    ''' Returns true if all contracts checks are disabled. '''
    return Switches.disable_all

