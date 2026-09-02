from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.tab import MDTabsBase


class SettingsTab(MDBoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(14)

        app = MDApp.get_running_app()
        settings = app.storage.load_settings()

        title = MDLabel(
            text="Configurações",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(48),
        )
        self.add_widget(title)

        theme_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(112),
            radius=[18, 18, 18, 18],
            elevation=2,
        )
        row = MDBoxLayout(orientation="horizontal")
        row.add_widget(MDLabel(text="Tema escuro", font_style="Subtitle1"))
        self.theme_switch = MDSwitch(active=settings.get("dark_mode", False))
        self.theme_switch.bind(active=self._theme_changed)
        row.add_widget(self.theme_switch)
        theme_card.add_widget(row)
        theme_card.add_widget(
            MDLabel(
                text="Sua escolha fica salva para a próxima abertura.",
                theme_text_color="Secondary",
                font_style="Caption",
            )
        )
        self.add_widget(theme_card)

        stroke_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(150),
            radius=[18, 18, 18, 18],
            elevation=2,
        )
        self.stroke_label = MDLabel(
            text=f"Espessura padrão: {float(settings.get('stroke_width', 4.0)):.0f}px",
            font_style="Subtitle1",
        )
        stroke_card.add_widget(self.stroke_label)
        self.stroke_slider = MDSlider(
            min=2,
            max=12,
            step=1,
            value=float(settings.get("stroke_width", 4.0)),
        )
        self.stroke_slider.bind(value=self._stroke_changed)
        stroke_card.add_widget(self.stroke_slider)
        self.add_widget(stroke_card)

        about = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(132),
            radius=[18, 18, 18, 18],
            elevation=2,
        )
        about.add_widget(MDLabel(text="GestureVoice Pro", font_style="H6", bold=True))
        about.add_widget(
            MDLabel(
                text="Versão 0.2.0",
                theme_text_color="Secondary",
                font_style="Body2",
            )
        )
        about.add_widget(
            MDLabel(
                text="Código aberto • armazenamento local • sem serviços pagos",
                theme_text_color="Secondary",
                font_style="Caption",
            )
        )
        self.add_widget(about)

    def _theme_changed(self, instance, value):
        MDApp.get_running_app().set_dark_mode(value)

    def _stroke_changed(self, instance, value):
        value = float(value)
        self.stroke_label.text = f"Espessura padrão: {value:.0f}px"
        MDApp.get_running_app().set_default_stroke_width(value)
