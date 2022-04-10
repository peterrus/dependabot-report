from dataclasses import dataclass, field


@dataclass
class Alert:
    package_ecosystem: str
    package_name: str
    permalink: str
    severity: str
    summary: str
    identifiers: list[dict] = field(default_factory=list)


@dataclass
class Repository:
    name: str
    organization_name: str
    alerts_open: str
    alerts_fixed: str
    alerts_dismissed: str
