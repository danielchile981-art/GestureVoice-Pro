__version__ = "0.2.1"

from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar

from screens.tabs import HomeScreen
from screens.gestures_screen import DrawingScreen
from utils.storage import StorageManager


class GestureVoiceProApp(MDApp):
    """Aplicativo principal do GestureVoice Pro."""

    def build(self):
        self.title = "GestureVoice Pro"
        self.storage = StorageManager(self.user_data_dir)

        settings = self.storage.load_settings()
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Dark" if settings.get("dark_mode", False) else "Light"

        self.screen_manager = ScreenManager(
            transition=SlideTransition(duration=0.22)
        )

        self.home_screen = HomeScreen(name="home")
        self.drawing_screen = DrawingScreen(name="drawing")

        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.drawing_screen)
        return self.screen_manager

    def on_start(self):
        self.home_screen.refresh_gestures()

    def open_drawing_screen(self):
        self.drawing_screen.prepare_new_gesture()
        self.screen_manager.transition.direction = "left"
        self.screen_manager.current = "drawing"

    def go_home(self, refresh=False):
        if refresh:
            self.home_screen.refresh_gestures()
        self.screen_manager.transition.direction = "right"
        self.screen_manager.current = "home"

    def show_snackbar(self, message):
        Snackbar(text=message, duration=2.4).open()

    def set_dark_mode(self, enabled):
        self.theme_cls.theme_style = "Dark" if enabled else "Light"
        settings = self.storage.load_settings()
        settings["dark_mode"] = bool(enabled)
        self.storage.save_settings(settings)

    def set_default_stroke_width(self, value):
        settings = self.storage.load_settings()
        settings["stroke_width"] = float(value)
        self.storage.save_settings(settings)


if __name__ == "__main__":
    GestureVoiceProApp().run()
