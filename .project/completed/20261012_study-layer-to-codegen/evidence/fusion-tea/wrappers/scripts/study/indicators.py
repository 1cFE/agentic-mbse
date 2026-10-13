"""An alias for the installed ``sysml_codegen.study.indicators``, where this module moved.

Importing ``scripts.study.indicators`` gives the installed module itself, and running this file,
by path or with ``-m``, runs that module's ``main()``. Either way, the study tools'
project root is first pinned to this repository, found from this file's location
as the original found it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.study import indicators as _moved
from sysml_codegen.study import roots as _roots

_roots.use_project_root(Path(__file__).resolve().parents[2])

if __name__ == "__main__":
    sys.exit(_moved.main())
sys.modules[__name__] = _moved
