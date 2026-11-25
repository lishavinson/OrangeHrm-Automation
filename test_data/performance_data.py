from datetime import datetime


def create_kpi_name(prefix: str = "Automation KPI") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix} {timestamp}"
