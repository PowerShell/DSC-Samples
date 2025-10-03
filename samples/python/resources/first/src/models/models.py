from dataclasses import dataclass, asdict
from typing import Literal, Optional

import json

@dataclass
class TsToy:
    scope: Literal["user", "machine"]
    _exist: bool = True
    updateAutomatically: Optional[bool] = None
    updateFrequency: Optional[int] = None
    
    def to_json(self, include_none: bool = False) -> str:
        data = asdict(self)   
        if not include_none:
            data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data)

    def to_dict(self, include_none: bool = False) -> dict:
        data = asdict(self)
        
        if not include_none:
            data = {k: v for k, v in data.items() if v is not None}
            
        return data