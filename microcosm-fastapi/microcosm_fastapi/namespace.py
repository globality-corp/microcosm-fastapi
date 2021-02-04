from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Namespace:
    subject: Any
    version: Optional[str] = None

    @property
    def path_prefix(self):
        return [
            part
            for part in [version, self.subject_name]
            if part
        ]

    @property
    def subject_name(self):
        return name_for(self.subject)
