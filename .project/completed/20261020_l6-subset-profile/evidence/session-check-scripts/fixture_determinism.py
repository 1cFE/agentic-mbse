"""Run each level standalone N times per fixture with no session; report fixtures whose result varies."""
import sys
sys.path.insert(0, "/home/reid/src/agentic-mbse/tests/test_validation")
from dotenv import load_dotenv
load_dotenv("/home/reid/src/agentic-mbse/.env")
from test_session import FIXTURES, LEVELS, SESSION_FIXTURES, result_view
names = SESSION_FIXTURES + ["sump_pump/right", "sump_pump/seed", "sump_pump/wrong"]
n = int(sys.argv[1])
for name in names:
    varying = [lvl for lvl in LEVELS if len({repr(result_view(lvl, FIXTURES / name)) for _ in range(n)}) > 1]
    print(f"{name}: {'varies at L' + str(varying) if varying else 'stable'}", flush=True)
