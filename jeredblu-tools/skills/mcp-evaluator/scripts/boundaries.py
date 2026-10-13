"""Small mitigation examples for stable trees; not a sandbox or race-proof file opener."""
from pathlib import Path
import re

def contained_file(root, user_path):
    base = Path(root).resolve(strict=True)
    if not base.is_dir():
        raise ValueError("root must be a directory")
    value = Path(user_path)
    if value.is_absolute():
        raise ValueError("absolute path refused")
    candidate = (base/value).resolve(strict=True)
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("path outside approved root") from exc
    if candidate == base or not candidate.is_file():
        raise ValueError("regular child file required")
    return candidate

def positive_integer(value, maximum):
    if type(maximum) is not int or maximum < 1:
        raise ValueError("maximum must be positive integer")
    if type(value) is int:
        parsed=value
    elif isinstance(value,str) and re.fullmatch(r"[0-9]+",value):
        if len(value)>12:
            raise ValueError("numeric value too long")
        parsed=int(value)
    else:
        raise ValueError("expected complete integer")
    if not 1<=parsed<=maximum:
        raise ValueError("integer out of range")
    return parsed
