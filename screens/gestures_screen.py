from datetime import datetime

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDFloatingActionButton,
    MDFlatButton,
    MDRaisedButton,
    MDIconButton,
)
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.slider import MDSlider
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

from models.gesture import Gesture
from utils.animations import fade_in


class NameDialogContent(MDBoxLayout):
    def __init__(self, initial_text="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(92)
        self.padding = (0, dp(8), 0, 0)

        self.field = MDTextField(
            hint_text="Nome do gesto",
            text=initial_text,
            mode="rectangle",
            max_text_length=40,
        )
        self.add_widget(self.field)


class GesturePreview(Widget):
    """Miniatura leve do gesto usando coordenadas normalizadas."""

    def __init__(self, strokes=None, **kwargs):
        super().__init__(**kwargs)
        self.strokes = strokes or []
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return

        with self.canvas:
            Color(0.48, 0.20, 0.95, 1)
            for stroke in self.strokes:
                coords = []
                for point in stroke:
                    if len(point) < 2:
                        continue
                    x = self.x + float(point[0]) * self.width
                    y = self.y + float(point[1]) * self.height
                    coords += [x, y]
                if len(coords) >= 4:
                    Line(points=coords, width=1.5)


class GestureDrawingWidget(Widget):
    """Canvas que preserva cada toque como um stroke separado."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw_strokes = []
        self.current_stroke = None
        self.current_line = None
        self.line_width = 4.0
        self.bind(pos=self._refresh_background, size=self._refresh_background)
        self._refresh_background()

    def _refresh_background(self, *args):
        # Redesenha fundo + strokes já existentes.
        strokes = [list(stroke) for stroke in self.raw_strokes]
        self.canvas.clear()
        with self.canvas:
            Color(0.12, 0.12, 0.16, 0.10)
            RoundedRectangle(
                pos=(self.x, self.y),
                size=(self.width, self.height),
                radius=[dp(18)],
            )
            Color(0.55, 0.20, 0.95, 1)
            for stroke in strokes:
                coords = []
                for lx, ly in stroke:
                    coords += [self.x + lx, self.y + ly]
                if len(coords) >= 4:
                    Line(points=coords, width=self.line_width)

    def _clamp_local(self, x, y):
        lx = max(0, min(x - self.x, self.width))
        ly = max(0, min(y - self.y, self.height))
        return lx, ly

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return super().on_touch_down(touch)

        touch.grab(self)
        lx, ly = self._clamp_local(touch.x, touch.y)
        self.current_stroke = [(lx, ly)]
        self.raw_strokes.append(self.current_stroke)

        with self.canvas:
            Color(0.55, 0.20, 0.95, 1)
            self.current_line = Line(
                points=[touch.x, touch.y],
                width=self.line_width,
            )
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_move(touch)

        lx, ly = self._clamp_local(touch.x, touch.y)
        self.current_stroke.append((lx, ly))
        if self.current_line:
            self.current_line.points += [self.x + lx, self.y + ly]
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_up(touch)

        touch.ungrab(self)
        lx, ly = self._clamp_local(touch.x, touch.y)
        self.current_stroke.append((lx, ly))
        if self.current_line:
            self.current_line.points += [self.x + lx, self.y + ly]

        self.current_stroke = None
        self.current_line = None
        return True

    def set_line_width(self, value):
        self.line_width = float(value)
        self._refresh_background()

    def clear_drawing(self):
        self.raw_strokes = []
        self.current_stroke = None
        self.current_line = None
        self._refresh_background()

    def undo_last_stroke(self):
        if self.raw_strokes:
            self.raw_strokes.pop()
            self._refresh_background()
            return True
        return False

    def point_count(self):
        return sum(len(stroke) for stroke in self.raw_strokes)

    def has_valid_gesture(self):
        # Evita salvar mero toque acidental.
        return self.point_count() >= 8

    def get_normalized_strokes(self):
        if self.width <= 0 or self.height <= 0:
            return []

        result = []
        for stroke in self.raw_strokes:
            normalized_stroke = []
            for x, y in stroke:
                nx = max(0.0, min(1.0, x / self.width))
                ny = max(0.0, min(1.0, y / self.height))
                normalized_stroke.append([round(nx, 6), round(ny, 6)])
            if normalized_stroke:
                result.append(normalized_stroke)
        return result


class DrawingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name_dialog = None
        self.cancel_dialog = None

        root = MDBoxLayout(orientation="vertical")

        root.add_widget(
            MDTopAppBar(
                title="Novo gesto",
                left_action_items=[["arrow-left", lambda x: self.cancel()]],
                elevation=3,
            )
        )

        self.hint = MDLabel(
            text="Desenhe o gesto com o dedo",
            halign="center",
            size_hint_y=None,
            height=dp(42),
            theme_text_color="Secondary",
        )
        root.add_widget(self.hint)

        canvas_card = MDCard(
            orientation="vertical",
            padding=dp(8),
            radius=[20, 20, 20, 20],
            elevation=2,
        )
        self.drawing_widget = GestureDrawingWidget()
        canvas_card.add_widget(self.drawing_widget)
        root.add_widget(canvas_card)

        controls = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=(dp(14), dp(6), dp(14), dp(10)),
            spacing=dp(6),
        )

        width_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
        )
        self.width_label = MDLabel(text="Traço: 4px", size_hint_x=0.32)
        self.width_slider = MDSlider(min=2, max=12, step=1, value=4)
        self.width_slider.bind(value=self._width_changed)
        width_row.add_widget(self.width_label)
        width_row.add_widget(self.width_slider)
        controls.add_widget(width_row)

        buttons = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(8),
        )

        undo = MDFlatButton(text="DESFAZER")
        clear = MDFlatButton(text="LIMPAR")
        cancel = MDFlatButton(text="CANCELAR")
        save = MDRaisedButton(text="SALVAR")

        undo.bind(on_release=lambda x: self.undo())
        clear.bind(on_release=lambda x: self.clear())
        cancel.bind(on_release=lambda x: self.cancel())
        save.bind(on_release=lambda x: self.ask_name())

        for button in (undo, clear, cancel, save):
            buttons.add_widget(button)

        controls.add_widget(buttons)
        root.add_widget(controls)
        self.add_widget(root)

    def prepare_new_gesture(self):
        app = MDApp.get_running_app()
        width = float(app.storage.load_settings().get("stroke_width", 4.0))
        self.width_slider.value = width
        self.drawing_widget.set_line_width(width)
        self.drawing_widget.clear_drawing()

    def _width_changed(self, instance, value):
        value = float(value)
        self.width_label.text = f"Traço: {value:.0f}px"
        self.drawing_widget.set_line_width(value)

    def undo(self):
        app = MDApp.get_running_app()
        if not self.drawing_widget.undo_last_stroke():
            app.show_snackbar("Nada para desfazer.")

    def clear(self):
        self.drawing_widget.clear_drawing()
        MDApp.get_running_app().show_snackbar("Área de desenho limpa.")

    def cancel(self):
        if not self.drawing_widget.raw_strokes:
            MDApp.get_running_app().go_home()
            return

        self.cancel_dialog = MDDialog(
            title="Descartar desenho?",
            text="O gesto atual ainda não foi salvo.",
            buttons=[
                MDFlatButton(
                    text="CONTINUAR",
                    on_release=lambda x: self.cancel_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="DESCARTAR",
                    on_release=lambda x: self._discard_and_exit(),
                ),
            ],
        )
        self.cancel_dialog.open()

    def _discard_and_exit(self):
        if self.cancel_dialog:
            self.cancel_dialog.dismiss()
        self.drawing_widget.clear_drawing()
        MDApp.get_running_app().go_home()

    def ask_name(self):
        app = MDApp.get_running_app()
        if not self.drawing_widget.has_valid_gesture():
            app.show_snackbar("Desenhe um gesto maior antes de salvar.")
            return

        content = NameDialogContent()
        self.name_dialog = MDDialog(
            title="Salvar gesto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.name_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SALVAR",
                    on_release=lambda x: self.save_gesture(content),
                ),
            ],
        )
        self.name_dialog.open()

    def save_gesture(self, content):
        app = MDApp.get_running_app()
        name = content.field.text.strip()

        if not name:
            app.show_snackbar("Digite um nome para o gesto.")
            return

        if app.storage.name_exists(name):
            app.show_snackbar("Já existe um gesto com esse nome.")
            return

        strokes = self.drawing_widget.get_normalized_strokes()
        points = [p for stroke in strokes for p in stroke]

        app.storage.add_gesture(
            Gesture(
                name=name,
                points=points,
                strokes=strokes,
                line_width=float(self.width_slider.value),
            )
        )

        if self.name_dialog:
            self.name_dialog.dismiss()

        self.drawing_widget.clear_drawing()
        app.go_home(refresh=True)
        app.show_snackbar(f'Gesto "{name}" salvo.')


class GestureCard(MDCard):
    def __init__(self, gesture, owner, **kwargs):
        super().__init__(**kwargs)
        self.gesture = gesture
        self.owner = owner

        self.orientation = "horizontal"
        self.padding = dp(12)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(112)
        self.radius = [18, 18, 18, 18]
        self.elevation = 2

        preview = GesturePreview(
            strokes=gesture.strokes,
            size_hint=(None, None),
            size=(dp(78), dp(78)),
        )
        self.add_widget(preview)

        text_box = MDBoxLayout(orientation="vertical")
        text_box.add_widget(
            MDLabel(
                text=gesture.name,
                font_style="Subtitle1",
                bold=True,
                shorten=True,
            )
        )
        text_box.add_widget(
            MDLabel(
                text=f"Criado em {owner.format_date(gesture.created_at)}",
                theme_text_color="Secondary",
                font_style="Caption",
            )
        )
        self.add_widget(text_box)

        actions = MDBoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(48),
        )
        play = MDIconButton(icon="play")
        edit = MDIconButton(icon="pencil")
        delete = MDIconButton(icon="delete-outline")

        play.bind(on_release=lambda x: owner.execute_gesture(gesture.gesture_id))
        edit.bind(on_release=lambda x: owner.open_edit_dialog(gesture.gesture_id))
        delete.bind(on_release=lambda x: owner.confirm_delete(gesture.gesture_id))

        actions.add_widget(play)
        actions.add_widget(edit)
        actions.add_widget(delete)
        self.add_widget(actions)


class GesturesTab(MDFloatLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_dialog = None
        self.delete_dialog = None

        root = MDBoxLayout(
            orientation="vertical",
            padding=(dp(12), dp(12), dp(12), dp(84)),
            spacing=dp(10),
        )

        self.header = MDLabel(
            text="Seus gestos",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(44),
        )
        root.add_widget(self.header)

        scroll = ScrollView()
        self.list_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
        )
        scroll.add_widget(self.list_box)
        root.add_widget(scroll)
        self.add_widget(root)

        fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={"right": 0.95, "y": 0.035},
        )
        fab.bind(on_release=lambda x: MDApp.get_running_app().open_drawing_screen())
        self.add_widget(fab)

    @staticmethod
    def format_date(value):
        try:
            date = datetime.fromisoformat(value)
            return date.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return value or "-"

    def refresh_list(self):
        if not hasattr(self, "list_box"):
            return

        self.list_box.clear_widgets()
        app = MDApp.get_running_app()
        gestures = app.storage.load_gestures()
        self.header.text = f"Seus gestos ({len(gestures)})"

        if not gestures:
            empty = MDCard(
                orientation="vertical",
                padding=dp(20),
                size_hint_y=None,
                height=dp(170),
                radius=[18, 18, 18, 18],
                elevation=1,
            )
            empty.add_widget(
                MDLabel(
                    text="Nenhum gesto salvo",
                    font_style="H6",
                    halign="center",
                )
            )
            empty.add_widget(
                MDLabel(
                    text="Toque no botão + para desenhar seu primeiro gesto.",
                    theme_text_color="Secondary",
                    halign="center",
                )
            )
            self.list_box.add_widget(empty)
            return

        for gesture in reversed(gestures):
            self.list_box.add_widget(GestureCard(gesture, self))

        fade_in(self.list_box)

    def execute_gesture(self, gesture_id):
        app = MDApp.get_running_app()
        gesture = app.storage.get_gesture(gesture_id)
        if gesture:
            app.show_snackbar(f'Executando gesto "{gesture.name}"')

    def open_edit_dialog(self, gesture_id):
        app = MDApp.get_running_app()
        gesture = app.storage.get_gesture(gesture_id)
        if not gesture:
            return

        content = NameDialogContent(initial_text=gesture.name)
        self.edit_dialog = MDDialog(
            title="Renomear gesto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.edit_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SALVAR",
                    on_release=lambda x: self.save_rename(
                        gesture_id, content
                    ),
                ),
            ],
        )
        self.edit_dialog.open()

    def save_rename(self, gesture_id, content):
        app = MDApp.get_running_app()
        name = content.field.text.strip()

        if not name:
            app.show_snackbar("O nome não pode ficar vazio.")
            return

        if app.storage.name_exists(name, exclude_id=gesture_id):
            app.show_snackbar("Já existe outro gesto com esse nome.")
            return

        if app.storage.rename_gesture(gesture_id, name):
            self.edit_dialog.dismiss()
            self.refresh_list()
            app.show_snackbar("Gesto renomeado.")

    def confirm_delete(self, gesture_id):
        app = MDApp.get_running_app()
        gesture = app.storage.get_gesture(gesture_id)
        if not gesture:
            return

        self.delete_dialog = MDDialog(
            title="Excluir gesto?",
            text=f'O gesto "{gesture.name}" será apagado do aparelho.',
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.delete_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="EXCLUIR",
                    on_release=lambda x: self.delete_gesture(gesture_id),
                ),
            ],
        )
        self.delete_dialog.open()

    def delete_gesture(self, gesture_id):
        app = MDApp.get_running_app()
        if app.storage.delete_gesture(gesture_id):
            if self.delete_dialog:
                self.delete_dialog.dismiss()
            self.refresh_list()
            app.show_snackbar("Gesto excluído.")
