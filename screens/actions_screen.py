from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase


class ActionsTab(MDBoxLayout, MDTabsBase):
    """Placeholder mantido para as ações avançadas das próximas etapas."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "24dp"

        self.add_widget(
            MDLabel(
                text="Funcionalidade será adicionada na Fase 2",
                halign="center",
                valign="middle",
                font_style="H6",
            )
        )
