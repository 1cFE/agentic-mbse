"""An alias for the installed ``sysml_codegen.study.identity``, where this module moved.

Importing ``scripts.study.identity`` gives the installed module itself. The study tools'
project root is first pinned to this repository, found from this file's location
as the original found it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.study import identity as _moved
from sysml_codegen.study import roots as _roots

_roots.use_project_root(Path(__file__).resolve().parents[2])

if __name__ != "__main__":
    sys.modules[__name__] = _moved
