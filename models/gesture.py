from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Gesture:
    name: str
    points: list = field(default_factory=list)
    strokes: list = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    gesture_id: str = ""
    line_width: float = 4.0

    def __post_init__(self):
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        if not self.gesture_id:
            self.gesture_id = str(uuid4())
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = self.created_at

        # Compatibilidade: se um gesto antigo tiver apenas points,
        # converte para um único stroke.
        if not self.strokes and self.points:
            self.strokes = [self.points]

        # Mantém "points" também para compatibilidade com o formato original.
        if not self.points and self.strokes:
            self.points = [p for stroke in self.strokes for p in stroke]

    def touch_updated_at(self):
        self.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "id": self.gesture_id,
            "name": self.name,
            "points": self.points,
            "strokes": self.strokes,
            "line_width": self.line_width,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            gesture_id=data.get("id", ""),
            name=data.get("name", "Sem nome"),
            points=data.get("points", []),
            strokes=data.get("strokes", []),
            line_width=float(data.get("line_width", 4.0)),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", data.get("created_at", "")),
        )
