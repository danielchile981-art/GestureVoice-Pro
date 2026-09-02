from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabs
from kivymd.uix.toolbar import MDTopAppBar

from screens.gestures_screen import GesturesTab
from screens.actions_screen import ActionsTab
from screens.settings_screen import SettingsTab


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = MDBoxLayout(orientation="vertical")

        root.add_widget(
            MDTopAppBar(
                title="GestureVoice Pro",
                elevation=3,
            )
        )

        self.tabs = MDTabs()
        self.gestures_tab = GesturesTab(title="Gestos")
        self.actions_tab = ActionsTab(title="Ações")
        self.settings_tab = SettingsTab(title="Configurações")

        self.tabs.add_widget(self.gestures_tab)
        self.tabs.add_widget(self.actions_tab)
        self.tabs.add_widget(self.settings_tab)
        self.tabs.bind(on_tab_switch=self.on_tab_switch)

        root.add_widget(self.tabs)
        self.add_widget(root)

    def on_tab_switch(self, tabs, tab, *args):
        if tab is self.gestures_tab:
            self.refresh_gestures()

    def refresh_gestures(self):
        self.gestures_tab.refresh_list()
