import pandas as pd
from typing import List
from pathlib import Path
from src.models.experiment import HealthEvent

class HealthParser:  # Renamed from HealthCheckParser
    def parse(self, csv_path: Path) -> List[HealthEvent]:
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        events = []
        for _, row in df.iterrows():
            # Handle NaN values - convert to None or empty string
            def clean_value(val, default=""):
                if pd.isna(val):
                    return default
                return str(val)
            
            he = HealthEvent(
                timestamp=row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
                service=clean_value(row.get("application") or row.get("service")),
                url=clean_value(row.get("url")),
                status_code=int(row["status_code"]) if pd.notna(row.get("status_code")) else None,
                latency_ms=float(row["latency_ms"]) if pd.notna(row.get("latency_ms")) else None,
                healthy=bool(row["healthy"]) if pd.notna(row.get("healthy")) else True,
                error=clean_value(row.get("error")) or None,
            )
            events.append(he)
        return events
