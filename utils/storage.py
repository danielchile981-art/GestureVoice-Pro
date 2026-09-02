import json
import os
from models.gesture import Gesture


class StorageManager:
    """Leitura/escrita atômica de gestos e preferências."""

    SCHEMA_VERSION = 2

    def __init__(self, base_dir):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.gestures_path = os.path.join(self.base_dir, "gestures.json")
        self.settings_path = os.path.join(self.base_dir, "settings.json")

    @staticmethod
    def _read_json(path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return default

    @staticmethod
    def _write_json(path, data):
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.flush()
            try:
                os.fsync(file.fileno())
            except OSError:
                pass
        os.replace(temp_path, path)

    def load_gestures(self):
        data = self._read_json(
            self.gestures_path,
            {"schema_version": self.SCHEMA_VERSION, "gestures": []},
        )
        result = []
        for item in data.get("gestures", []):
            try:
                result.append(Gesture.from_dict(item))
            except Exception:
                continue
        return result

    def save_gestures(self, gestures):
        self._write_json(
            self.gestures_path,
            {
                "schema_version": self.SCHEMA_VERSION,
                "gestures": [gesture.to_dict() for gesture in gestures],
            },
        )

    def add_gesture(self, gesture):
        gestures = self.load_gestures()
        gestures.append(gesture)
        self.save_gestures(gestures)

    def get_gesture(self, gesture_id):
        for gesture in self.load_gestures():
            if gesture.gesture_id == gesture_id:
                return gesture
        return None

    def name_exists(self, name, exclude_id=None):
        normalized = name.strip().casefold()
        return any(
            g.name.strip().casefold() == normalized and g.gesture_id != exclude_id
            for g in self.load_gestures()
        )

    def rename_gesture(self, gesture_id, new_name):
        gestures = self.load_gestures()
        for gesture in gestures:
            if gesture.gesture_id == gesture_id:
                gesture.name = new_name.strip()
                gesture.touch_updated_at()
                self.save_gestures(gestures)
                return True
        return False

    def delete_gesture(self, gesture_id):
        gestures = self.load_gestures()
        new_gestures = [g for g in gestures if g.gesture_id != gesture_id]
        if len(new_gestures) == len(gestures):
            return False
        self.save_gestures(new_gestures)
        return True

    def load_settings(self):
        return self._read_json(
            self.settings_path,
            {
                "dark_mode": False,
                "stroke_width": 4.0,
            },
        )

    def save_settings(self, settings):
        defaults = {
            "dark_mode": False,
            "stroke_width": 4.0,
        }
        defaults.update(settings or {})
        self._write_json(self.settings_path, defaults)
