from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MeasurementResult:
    value: float
    timestamp: Optional[datetime] = None
