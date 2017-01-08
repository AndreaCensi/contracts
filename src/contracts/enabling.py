from . import logger
import os


class Switches:
    # default to ENV variable
    disable_all = os.environ.get('DISABLE_CONTRACTS', False)


def disable_all():
    """ Disables all contracts checks. """
#     print('disable_all()')
    Switches.disable_all = True
    logger.info('All contracts checking disabled.')


def enable_all():
    """
    Enables all contracts checks.
    Can be overridden by an environment variable.
    """
#     print('enable_all()')
    if not os.environ.get('DISABLE_CONTRACTS', False):
        Switches.disable_all = False
        logger.info('All contracts checking enabled.')


def all_disabled():
#     print('all_Disabled? %s' % Switches.disable_all)
    """ Returns true if all contracts checks are disabled. """
    return Switches.disable_all

