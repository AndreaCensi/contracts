##############################################################################
# Modified to work as a lightweight alternative to vendoring six.
# Originally from the package RestrictedPython.
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import platform
import sys

_version = sys.version_info
IS_PY2 = _version.major == 2
IS_PY3 = _version.major == 3
IS_PY34_OR_GREATER = _version.major == 3 and _version.minor >= 4
IS_PY35_OR_GREATER = _version.major == 3 and _version.minor >= 5
IS_PY36_OR_GREATER = _version.major == 3 and _version.minor >= 6
IS_PY37_OR_GREATER = _version.major == 3 and _version.minor >= 7
IS_PY38_OR_GREATER = _version.major == 3 and _version.minor >= 8
IS_PY3A_OR_GREATER = _version.major == 3 and _version.minor >= 10

if IS_PY2:  # pragma: no cover
    basestring = basestring  # NOQA: F821  # Python 2 only built-in function
else:  # pragma: PY3
    basestring = str

if IS_PY2:  # pragma: no cover
    unicode = unicode # NOQA: F821  # Python 2 only built-in function
else:
    unicode = str

IS_CPYTHON = platform.python_implementation() == 'CPython'
