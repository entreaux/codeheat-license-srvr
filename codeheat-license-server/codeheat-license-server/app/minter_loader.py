import base64
import importlib.util
from pathlib import Path
from types import ModuleType
from .config import settings

PRIVATE_MINTER_PATH = Path("private/license_minter.py")

def _import_module_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("license_minter", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load minter module.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def load_mint_function():
    """
    Must return callable:
      mint_license(email, tier, license_id, session_id) -> dict(payload, signature)
    """
    # 1) local private file
    if PRIVATE_MINTER_PATH.exists():
        mod = _import_module_from_path(PRIVATE_MINTER_PATH)
        if not hasattr(mod, "mint_license"):
            raise RuntimeError("private/license_minter.py must define mint_license(...)")
        return mod.mint_license

    # 2) env-injected minter
    b64 = settings.LICENSE_MINTER_PY_B64
    if not b64:
        raise RuntimeError(
            "No minter found. Provide private/license_minter.py locally OR set LICENSE_MINTER_PY_B64 on Railway."
        )
    code = base64.b64decode(b64.encode("utf-8")).decode("utf-8")

    tmp = Path("/tmp/license_minter.py")
    tmp.write_text(code, encoding="utf-8")

    mod = _import_module_from_path(tmp)
    if not hasattr(mod, "mint_license"):
        raise RuntimeError("Injected minter must define mint_license(...)")
    return mod.mint_license
