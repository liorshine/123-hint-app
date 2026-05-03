import numpy as np
import colorsys

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from ai import best_move
from game_logic import *


# 🎨 COLOR (auto mở rộng)
def get_color(val):
    if val == 0:
        return "#cdc1b4"

    level = int(np.log2(val))

    base_colors = [
        "#eee4da","#ede0c8","#f2b179","#f59563",
        "#f67c5f","#f65e3b","#edcf72","#edcc61",
        "#edc850","#edc53f","#edc22e"
    ]

    if level-1 < len(base_colors):
        return base_colors[level-1]

    # tạo màu mới
    h = (level * 0.08) % 1
    r, g, b = colorsys.hsv_to_rgb(h, 0.6, 0.95)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))


def hex_to_rgba(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0,2,4)) + (1,)


# 🔢 HIỂN THỊ LEVEL
def display_level(val):
    if val == 0:
        return ""
    return str(int(np.log2(val)))


class Game(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)

        self.board = np.zeros((4,4), dtype=int)
        self.selected = None
        self.suggested = None

        # ===== TITLE =====
        self.add_widget(Label(
            text="2048 AI Pro",
            font_size=28,
            bold=True,
            size_hint=(1, 0.1),
            color=(0.47, 0.43, 0.39, 1)
        ))

        # ===== MESSAGE =====
        self.message = Label(
            text="Chọn ô để đặt",
            size_hint=(1, 0.08),
            color=(0.3,0.3,0.3,1)
        )
        self.add_widget(self.message)

        # ===== GRID =====
        self.grid = GridLayout(cols=4, size_hint=(1, 0.65), spacing=10, padding=10)
        self.buttons = []

        for i in range(4):
            row = []
            for j in range(4):
                btn = Button(
                    text="",
                    font_size=24,
                    bold=True,
                    color=(0,0,0,1),
                    background_normal=""
                )
                btn.bind(on_press=lambda b, x=i, y=j: self.select(x,y))
                self.grid.add_widget(btn)
                row.append(btn)
            self.buttons.append(row)

        self.add_widget(self.grid)

        # ===== CONTROL =====
        control = GridLayout(cols=3, size_hint=(1, 0.17), spacing=10)

        def style(btn, color):
            btn.background_normal = ""
            btn.background_color = color
            btn.color = (1,1,1,1)

        self.btn_place = Button(text="Place")
        self.btn_delete = Button(text="Delete")
        self.btn_reset = Button(text="Reset")
        self.btn_hint = Button(text="Hint")
        self.btn_apply = Button(text="Apply")

        style(self.btn_place, (0.56, 0.48, 0.40, 1))
        style(self.btn_delete, (0.8, 0.3, 0.3, 1))
        style(self.btn_reset, (0.3, 0.6, 0.9, 1))
        style(self.btn_hint, (0.56, 0.48, 0.40, 1))
        style(self.btn_apply, (0.56, 0.48, 0.40, 1))

        self.btn_place.bind(on_press=self.place_tile)
        self.btn_delete.bind(on_press=self.delete_tile)
        self.btn_reset.bind(on_press=self.reset_board)
        self.btn_hint.bind(on_press=self.get_hint)
        self.btn_apply.bind(on_press=self.apply_move)

        control.add_widget(self.btn_place)
        control.add_widget(self.btn_delete)
        control.add_widget(self.btn_reset)
        control.add_widget(self.btn_hint)
        control.add_widget(self.btn_apply)

        self.add_widget(control)

        self.draw()

    # ===== DRAW =====
    def draw(self):
        for i in range(4):
            for j in range(4):
                val = self.board[i][j]
                btn = self.buttons[i][j]

                btn.text = display_level(val)
                btn.background_color = hex_to_rgba(get_color(val))

                if self.selected == (i,j):
                    btn.background_color = (1,0,0,1)

    # ===== SELECT =====
    def select(self, x, y):
        self.selected = (x,y)
        self.message.text = f"Đã chọn ({x},{y})"
        self.draw()

    # ===== PLACE =====
    def place_tile(self, instance):
        if not self.selected:
            self.message.text = "Chọn ô trước"
            return

        x, y = self.selected

        if self.board[x][y] != 0:
            self.message.text = "Ô đã có số"
            return

        layout = GridLayout(cols=5, spacing=10, padding=10)
        popup = Popup(title="Chọn Level (1-20)", size_hint=(0.9, 0.6))

        for i in range(1,21):
            btn = Button(text=str(i))

            def choose(btn, level=i):
                self.board[x][y] = 2 ** level
                self.message.text = f"Đặt level {level}"
                self.selected = None
                self.draw()
                popup.dismiss()

            btn.bind(on_press=choose)
            layout.add_widget(btn)

        popup.content = layout
        popup.open()

    # ===== DELETE =====
    def delete_tile(self, instance):
        if not self.selected:
            self.message.text = "Chọn ô để xóa"
            return

        x, y = self.selected
        self.board[x][y] = 0
        self.selected = None
        self.message.text = "Đã xóa"
        self.draw()

    # ===== RESET =====
    def reset_board(self, instance):
        self.board = np.zeros((4,4), dtype=int)
        self.selected = None
        self.suggested = None
        self.message.text = "Đã reset"
        self.draw()

    # ===== HINT =====
    def get_hint(self, instance):
        move = best_move(self.board)
        self.suggested = move
        self.message.text = f"Gợi ý: {move}"

    # ===== APPLY =====
    def apply_move(self, instance):
        if not self.suggested:
            return

        move = self.suggested

        if move == "up":
            self.board = move_up(self.board)
        elif move == "down":
            self.board = move_down(self.board)
        elif move == "left":
            self.board = move_left(self.board)
        elif move == "right":
            self.board = move_right(self.board)

        self.suggested = None
        self.message.text = "Vui lòng đặt ô mới"
        self.draw()


class MyApp(App):
    def build(self):
        return Game()


if __name__ == "__main__":
    MyApp().run()