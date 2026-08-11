import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
src_dir = os.path.join(backend_dir, "src")

for d in (src_dir, backend_dir, root_dir):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from src.telephony.outbound.dial import main
except ModuleNotFoundError:
    from telephony.outbound.dial import main

if __name__ == "__main__":
    main()
