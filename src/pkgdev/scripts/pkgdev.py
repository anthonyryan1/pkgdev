"""collection of tools for Gentoo development and maintenance

pkgdev provides a collection of tools for Gentoo development and maintenance.
"""

from pkgcore.util import commandline

argparser = commandline.ArgumentParser(
    description=__doc__, help=False, script=(__file__, __name__))

subparsers = argparser.add_subparsers()
subparsers.add_command('commit')
subparsers.add_command('manifest')
subparsers.add_command('push')
