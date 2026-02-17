import base64
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("Usage: python scripts/b64_encode_file.py path/to/file.py")
    raise SystemExit(1)

p = Path(sys.argv[1])
data = p.read_bytes()
print(base64.b64encode(data).decode("utf-8"))
