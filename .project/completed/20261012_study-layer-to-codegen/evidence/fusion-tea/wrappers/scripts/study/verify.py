"""An alias for the installed ``sysml_codegen.study.verify``, where this module moved.

Importing ``scripts.study.verify`` gives the installed module itself, and running this file,
by path or with ``-m``, runs that module's ``main()``. Either way, the study tools'
project root is first pinned to this repository, found from this file's location
as the original found it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.study import roots as _roots
from sysml_codegen.study import verify as _moved

_roots.use_project_root(Path(__file__).resolve().parents[2])

if __name__ == "__main__":
    sys.exit(_moved.main())
sys.modules[__name__] = _moved
