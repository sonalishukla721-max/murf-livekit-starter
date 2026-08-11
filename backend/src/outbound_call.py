import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
for d in (current_dir, backend_dir):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from src.telephony.outbound.dial import main
except ModuleNotFoundError:
    from telephony.outbound.dial import main

if __name__ == "__main__":
    main()
