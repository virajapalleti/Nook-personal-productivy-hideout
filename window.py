import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QScrollArea, QSizeGrip, QApplication,
    QDialog, QLabel, QToolTip
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
import data as datastore

FONT = "Helvetica"

# ── Colour presets — edit these yourself ────────────────────────────
BG_PRESETS = [
    # darks
    ("#0a0a0a", "Black"),
    ("#121212", "Charcoal"),
    ("#1e1e1e", "Graphite"),
    ("#2b2d42", "Slate"),
    ("#0d1b2a", "Navy"),
    ("#003049", "Navy02"),
    ("#16213e", "Deep Ocean"),
    ("#1a1a2e", "Midnight"),
    ("#231942", "Indigo Night"),
    ("#3c1642", "Grape"),
    ("#1f0021", "Deep Wine"),
    ("#2d132c", "Dark Plum"),
    ("#3d0000", "Maroon"),
    ("#402218", "Espresso"),
    ("#1b3022", "Forest"),
    ("#0f3d3e", "Pine"),
    ("#264653", "Teal Night"),
    ("#3a5a40", "Dark Green"),
    ("#8364e8", "Purple"),
    ("#8d99ae", "Light Grey"),
    # lights
    ("#a3b18a", "Sage Green"),
    ("#d8e2dc", "Sage Mist"),
    ("#dbe7e4", "Mist"),
    ("#e2ece9", "Seafoam"),
    ("#caf0f8", "Light Blue"),
    ("#cddafd", "Periwinkle"),
    ("#e6e6fa", "Lavender"),
    ("#ffe5ec", "Blush"),
    ("#f7cad0", "Light Pink"),
    ("#fff1e6", "Peach"),
    ("#f4e1d2", "Sand"),
    ("#faf3dd", "Vanilla"),
    ("#fdf6e3", "Cream"),
    ("#e8e8e4", "Fog"),
    ("#f0f0f0", "White"),
]

def theme_for(bg):
    """Derive readable text/border colours from the background so light
    presets (White, Light Pink, ...) don't render invisible dark-theme text."""
    c = QColor(bg)
    luma = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
    if luma > 150:  # light background
        return {
            "text": "#1a1a1a",        # main task text
            "done": "#9a9a9a",        # completed task text
            "border": "#b9b9b9",      # header / divider borders
            "input_border": "#ababab",
            "placeholder": "#8a8a8a",
            "dim": "#7a7a7a",         # secondary buttons (x, clear, gear)
            "hover_bg": "rgba(0, 0, 0, 0.07)",
            "header_bg": "rgba(0, 0, 0, 0.04)",   # subtle fill behind category headers
            "row_hover": "rgba(0, 0, 0, 0.05)",   # task row hover highlight
            "scroll": "rgba(0, 0, 0, 0.18)",      # scrollbar handle
        }
    return {  # dark background — original palette
        "text": "#cccccc",
        "done": "#505050",
        "border": "#2a2a2a",
        "input_border": "#2f2f2f",
        "placeholder": "#444444",
        "dim": "#555555",
        "hover_bg": "#1a1a1a",
        "header_bg": "rgba(255, 255, 255, 0.03)",
        "row_hover": "rgba(255, 255, 255, 0.04)",
        "scroll": "rgba(255, 255, 255, 0.14)",
    }


ACCENT_PRESETS = [
    # warm
    ("#ff6b6b", "Red"),
    ("#f28482", "Salmon"),
    ("#e76f51", "Coral"),
    ("#f4a261", "Tangerine"),
    ("#ff9e00", "Amber"),
    ("#ffd166", "Sunflower"),
    ("#f0c040", "Gold"),
    ("#e9c46a", "Honey"),
    ("#dda15e", "Ochre"),
    ("#d4a373", "Caramel"),
    ("#e7bc91", "Light Brown"),
    ("#f5cac3", "Rose"),
    # cool
    ("#4ec9b0", "Mint"),
    ("#06d6a0", "Emerald"),
    ("#2a9d8f", "Teal"),
    ("#80ffdb", "Aqua"),
    ("#84a59d", "Eucalyptus"),
    ("#b7e4c7", "Light Green"),
    ("#90e0ef", "Ice Blue"),
    ("#7ec8e3", "Sky"),
    ("#118ab2", "Cerulean"),
    # purples & pinks
    ("#a78bfa", "Violet"),
    ("#c77dff", "Orchid"),
    ("#b5179e", "Fuchsia"),
    ("#f72585", "Magenta"),
    ("#34073d", "Deep purple"),
    # neutrals
    ("#0e1c26", "Black"),
    ("#d9dace", "Pale White"),
    ("#ffffff", "White"),
]
# ────────────────────────────────────────────────────────────────────


# ── Custom painted gear button (no emoji) ───────────────────────────
class GearButton(QPushButton):
    def __init__(self, accent="#555", base="#555"):
        super().__init__()
        self.setFixedSize(26, 26)
        self._base  = base
        self._hover = accent
        self._hovering = False
        self.setStyleSheet("background: transparent; border: none;")

    def set_accent(self, accent):
        self._hover = accent
        self.update()

    def enterEvent(self, e):
        self._hovering = True
        self.update()

    def leaveEvent(self, e):
        self._hovering = False
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self._hover if self._hovering else self._base)
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)

        cx, cy   = 13.0, 13.0
        n_teeth  = 6
        r_outer  = 5.8
        r_inner  = 4.2
        r_hole   = 2.1

        pts = []
        for i in range(n_teeth * 2):
            angle = math.pi * 2 * i / (n_teeth * 2)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))

        p.drawPolygon(QPolygonF(pts))
        p.drawEllipse(QPointF(cx, cy), r_hole, r_hole)
        p.end()


# ── Task item ────────────────────────────────────────────────────────
class TaskItem(QWidget):
    def __init__(self, task, accent, theme, on_change, on_delete, edit_mode=False):
        super().__init__()
        self.task      = task
        self.accent    = accent
        self.theme     = theme
        self.on_change = on_change
        self.on_delete = on_delete
        self.edit_mode = edit_mode
        # soft rounded hover highlight on the whole row
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            TaskItem {{ background: transparent; border-radius: 5px; }}
            TaskItem:hover {{ background: {theme["row_hover"]}; }}
        """)
        self.build()

    def build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        from PyQt6.QtWidgets import QCheckBox
        self.cb = QCheckBox()
        self.cb.setChecked(self.task["done"])
        self.cb.stateChanged.connect(self.toggle_done)
        layout.addWidget(self.cb)

        self.label = QLineEdit(self.task["text"])
        self.label.setReadOnly(True)
        self.label.mousePressEvent = lambda e: self.start_edit()
        self.label.returnPressed.connect(self.finish_edit)
        layout.addWidget(self.label)

        if self.edit_mode:
            del_btn = QPushButton("x")
            del_btn.setFixedSize(20, 20)
            del_btn.clicked.connect(self.on_delete)
            del_btn.setStyleSheet(f"""
                QPushButton {{ color: {self.theme["dim"]}; background: transparent; border: none; font-size: 12px; }}
                QPushButton:hover {{ color: #ff5555; }}
            """)
            layout.addWidget(del_btn)

        self.apply_style()

    def apply_style(self):
        done       = self.task["done"]
        text_color = self.theme["done"] if done else self.theme["text"]
        strike     = "line-through" if done else "none"
        self.label.setStyleSheet(f"""
            QLineEdit {{
                color: {text_color};
                text-decoration: {strike};
                background: transparent;
                border: none;
                font-family: {FONT};
                font-size: 12px;
                selection-background-color: {self.accent};
                selection-color: #ffffff;
            }}
        """)
        self.cb.setStyleSheet(f"""
            QCheckBox {{ background: transparent; }}
            QCheckBox::indicator {{
                width: 13px; height: 13px;
                border: 1px solid {self.accent};
                border-radius: 4px;
                background: transparent;
            }}
            QCheckBox::indicator:hover {{ border: 1.5px solid {self.accent}; }}
            QCheckBox::indicator:checked {{ background: {self.accent}; border: 1px solid {self.accent}; }}
        """)

    def toggle_done(self):
        self.task["done"] = self.cb.isChecked()
        self.apply_style()
        self.on_change()

    def start_edit(self):
        self.label.setReadOnly(False)
        self.label.setFocus()

    def finish_edit(self):
        text = self.label.text().strip()
        if text:
            self.task["text"] = text
        self.label.setReadOnly(True)
        self.apply_style()
        self.on_change()


# ── Category widget ──────────────────────────────────────────────────
class CategoryWidget(QWidget):
    def __init__(self, cat, accent, theme, on_change, on_delete_self,
                 edit_mode=False, expanded=False, two_col=False):
        super().__init__()
        self.cat           = cat
        self.accent        = accent
        self.theme         = theme
        self.on_change     = on_change
        self.on_delete_self = on_delete_self
        self.edit_mode     = edit_mode
        self.expanded      = expanded
        self.two_col       = two_col
        self.setStyleSheet("background: transparent;")
        self.build()

    def build(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 4)
        self.main_layout.setSpacing(2)

        header_row = QHBoxLayout()
        done  = sum(1 for t in self.cat["tasks"] if t["done"])
        total = len(self.cat["tasks"])

        self.header_btn = QPushButton(f"  {self.cat['name']}   {done}/{total}")
        self.header_btn.clicked.connect(self.toggle_expand)
        self._style_header()
        header_row.addWidget(self.header_btn)

        if self.edit_mode:
            del_btn = QPushButton("x")
            del_btn.setFixedSize(24, 24)
            del_btn.clicked.connect(self.on_delete_self)
            del_btn.setStyleSheet(f"""
                QPushButton {{ color: {self.theme["dim"]}; background: transparent; border: none; font-size: 13px; }}
                QPushButton:hover {{ color: #ff5555; }}
            """)
            header_row.addWidget(del_btn)

        self.main_layout.addLayout(header_row)

        self.task_area = QVBoxLayout()
        self.task_area.setSpacing(1)
        self.main_layout.addLayout(self.task_area)

        if self.expanded:
            self.refresh_tasks()

    def _style_header(self):
        # thin left-accent border, no bold
        self.header_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme["header_bg"]};
                color: {self.accent};
                border: 1px solid {self.theme["border"]};
                border-left: 2px solid {self.accent};
                border-radius: 6px;
                padding: 5px 8px;
                text-align: left;
                font-family: {FONT};
                font-size: 13px;
                font-weight: normal;
            }}
            QPushButton:hover {{ background: {self.theme["hover_bg"]}; }}
            QPushButton:pressed {{ background: {self.theme["header_bg"]}; }}
        """)

    def update_count(self):
        done  = sum(1 for t in self.cat["tasks"] if t["done"])
        total = len(self.cat["tasks"])
        self.header_btn.setText(f"  {self.cat['name']}   {done}/{total}")

    def toggle_expand(self):
        self.expanded = not self.expanded
        self.on_change(expand_toggle=True)

    def set_two_col(self, val):
        if val != self.two_col:
            self.two_col = val
            if self.expanded:
                self.refresh_tasks()

    def refresh_tasks(self):
        while self.task_area.count():
            item = self.task_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        self.update_count()

        if not self.expanded:
            return

        tasks = self.cat["tasks"]

        if self.two_col and len(tasks) > 0:
            grid = QGridLayout()
            grid.setSpacing(2)
            for i, task in enumerate(tasks):
                w = TaskItem(
                    task, self.accent, self.theme,
                    lambda: self.on_change(),
                    lambda checked=False, t=task: self.delete_task(t),
                    self.edit_mode
                )
                grid.addWidget(w, i // 2, i % 2)
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            container.setLayout(grid)
            self.task_area.addWidget(container)
        else:
            for task in tasks:
                w = TaskItem(
                    task, self.accent, self.theme,
                    lambda: self.on_change(),
                    lambda checked=False, t=task: self.delete_task(t),
                    self.edit_mode
                )
                self.task_area.addWidget(w)

        # task input — color set so typed text is visible, placeholder stays dim
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("new task")
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {self.theme["text"]};
                border: none;
                border-bottom: 1px solid {self.theme["input_border"]};
                padding: 4px 2px;
                font-family: {FONT};
                font-size: 12px;
                selection-background-color: {self.accent};
                selection-color: #ffffff;
            }}
            QLineEdit:focus {{ border-bottom: 1px solid {self.accent}; }}
        """)
        _p = self.task_input.palette()
        _p.setColor(_p.ColorRole.PlaceholderText, QColor(self.theme["placeholder"]))
        self.task_input.setPalette(_p)


        self.task_input.returnPressed.connect(self.add_task)
        self.task_area.addWidget(self.task_input)

        clear_btn = QPushButton("clear completed")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.theme["dim"]};
                background: transparent;
                border: none;
                font-size: 11px;
                font-family: {FONT};
                text-align: left;
                padding: 2px 0px;
            }}
            QPushButton:hover {{ color: {self.accent}; }}
        """)
        clear_btn.clicked.connect(self.clear_done)
        self.task_area.addWidget(clear_btn)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_task(self):
        text = self.task_input.text().strip()
        if not text:
            return
        self.cat["tasks"].append({"text": text, "done": False})
        self.task_input.clear()
        self.on_change()
        self.refresh_tasks()

    def delete_task(self, task):
        if task in self.cat["tasks"]:
            self.cat["tasks"].remove(task)
        self.on_change()
        self.refresh_tasks()

    def clear_done(self):
        self.cat["tasks"] = [t for t in self.cat["tasks"] if not t["done"]]
        self.on_change()
        self.refresh_tasks()


# ── Settings dialog — preset swatch grids ───────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent, accent, bg, on_accent, on_bg):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.accent    = accent
        self.bg        = bg
        self.on_accent = on_accent
        self.on_bg     = on_bg
        self.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                border: 1px solid #2e2e2e;
                border-radius: 10px;
            }
            QLabel {
                color: #555;
                font-size: 9px;
                font-family: Helvetica;
                letter-spacing: 1px;
            }
        """)
        self.build()

    PER_ROW = 10  # swatches per grid row

    def _swatch_row(self, label_text, presets, current, on_pick):
        """Labelled grid of clickable colour swatches (wraps every PER_ROW)."""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(wrapper)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(5)
        vl.addWidget(QLabel(label_text))

        row = QGridLayout()
        row.setSpacing(5)
        row.setContentsMargins(0, 0, 0, 0)

        for i, (hex_val, name) in enumerate(presets):
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.setToolTip(name)
            is_active = hex_val.lower() == current.lower()
            border = f"2px solid #ffffff" if is_active else "1px solid #333"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {hex_val};
                    border: {border};
                    border-radius: 6px;
                }}
                QPushButton:hover {{ border: 2px solid #aaaaaa; }}
            """)
            btn.clicked.connect(lambda checked=False, h=hex_val, fn=on_pick: (fn(h), self.close()))
            row.addWidget(btn, i // self.PER_ROW, i % self.PER_ROW)

        row.setColumnStretch(self.PER_ROW, 1)
        vl.addLayout(row)
        return wrapper

    def build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        layout.addWidget(self._swatch_row("ACCENT", ACCENT_PRESETS, self.accent, self.on_accent))
        layout.addWidget(self._swatch_row("BACKGROUND", BG_PRESETS, self.bg, self.on_bg))

        self.adjustSize()


# ── Main window ──────────────────────────────────────────────────────
class NookWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.data        = datastore.load()
        self.accent      = self.data.get("accent", "#4EC9B0")
        self.bg          = self.data.get("bg", "#1e1e1e")
        self.theme       = theme_for(self.bg)
        self.edit_mode   = False
        self._drag_pos   = None
        self._at_max_height = False
        self.cat_widgets = []
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setMinimumWidth(260)
        self.setMaximumWidth(300)
        self.setMinimumHeight(400)
        screen = QApplication.primaryScreen().availableGeometry()
        self.setMaximumHeight(screen.height() - 40)
        self.resize(260, 400)

        self.root = QWidget(self)
        self.root.setObjectName("nook_root")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.root)

        self.main_layout = QVBoxLayout(self.root)
        self.main_layout.setContentsMargins(12, 12, 12, 8)
        self.main_layout.setSpacing(6)

        self.apply_bg()
        self.build_ui()

    def apply_bg(self):
        self.root.setStyleSheet(f"""
            QWidget#nook_root {{
                background: {self.bg};
                border-radius: 10px;
                border: 1px solid {self.theme["border"]};
            }}
        """)

    def build_ui(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # top bar
        top_bar = QHBoxLayout()

        self.cat_input = QLineEdit()
        self.cat_input.setPlaceholderText("add category")
        self.cat_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {self.theme["text"]};
                border: none;
                border-bottom: 1px solid {self.theme["border"]};
                padding: 4px 2px;
                font-family: {FONT};
                font-size: 12px;
                selection-background-color: {self.accent};
                selection-color: #ffffff;
            }}
            QLineEdit:focus {{ border-bottom: 1px solid {self.accent}; }}
        """)
        _p = self.cat_input.palette()
        _p.setColor(_p.ColorRole.PlaceholderText, QColor(self.theme["placeholder"]))
        self.cat_input.setPalette(_p)

        self.cat_input.returnPressed.connect(self.add_category)
        top_bar.addWidget(self.cat_input)

        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(26, 26)
        edit_btn.setCheckable(True)
        edit_btn.setChecked(self.edit_mode)
        edit_btn.clicked.connect(self.toggle_edit_mode)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                color: {'#ff6b6b' if self.edit_mode else self.theme["dim"]};
                background: transparent;
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {self.accent}; }}
            QPushButton:checked {{ color: #ff6b6b; }}
        """)
        top_bar.addWidget(edit_btn)

        # clean painted gear — not an emoji
        self.gear_btn = GearButton(accent=self.accent, base=self.theme["dim"])
        self.gear_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(self.gear_btn)

        self.main_layout.addLayout(top_bar)

        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {self.theme['border']};")
        self.main_layout.addWidget(line)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # slim, rounded, themed scrollbar instead of the chunky OS default
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 2px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme["scroll"]};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {self.accent}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        """)

        self.cat_container = QWidget()
        self.cat_container.setStyleSheet("background: transparent;")
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setSpacing(5)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.addStretch()

        self.scroll.setWidget(self.cat_container)
        self.main_layout.addWidget(self.scroll)

        grip = QSizeGrip(self)
        grip.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(
            grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )

        self.render_categories()

    def render_categories(self):
        self.cat_widgets = []
        while self.cat_layout.count() > 1:
            item = self.cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        expanded_names = set(self.data.get("expanded", []))
        at_max = self._at_max_height

        for cat in self.data["categories"]:
            is_expanded = cat["name"] in expanded_names
            w = CategoryWidget(
                cat=cat,
                accent=self.accent,
                theme=self.theme,
                on_change=self.on_category_change,
                on_delete_self=self._make_delete_fn(cat),
                edit_mode=self.edit_mode,
                expanded=is_expanded,
                two_col=at_max
            )
            self.cat_layout.insertWidget(self.cat_layout.count() - 1, w)
            self.cat_widgets.append(w)

    def _make_delete_fn(self, cat):
        def delete():
            if cat in self.data["categories"]:
                self.data["categories"].remove(cat)
            self.save_and_render()
        return delete

    def on_category_change(self, expand_toggle=False):
        if expand_toggle:
            expanded = []
            for w in self.cat_widgets:
                if w.expanded:
                    expanded.append(w.cat["name"])
            self.data["expanded"] = expanded
            datastore.save(self.data)
            for w in self.cat_widgets:
                w.update_count()
            for w in self.cat_widgets:
                w.refresh_tasks()
        else:
            datastore.save(self.data)
            for w in self.cat_widgets:
                w.update_count()

    def save_and_render(self):
        datastore.save(self.data)
        if hasattr(self, 'cat_input'):
            self.cat_input.clear()
        self.render_categories()

    def add_category(self):
        name = self.cat_input.text().strip()
        if not name:
            return
        # expanded state is keyed by category name, so duplicates would
        # collide — reject a name that already exists
        if any(c["name"].lower() == name.lower() for c in self.data["categories"]):
            self.cat_input.selectAll()
            return
        self.data["categories"].append({"name": name, "tasks": []})
        self.cat_input.clear()
        self.save_and_render()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.build_ui()

    def open_settings(self):
        dlg = SettingsDialog(
            self,
            self.accent,
            self.bg,
            on_accent=self.set_accent,
            on_bg=self.set_bg
        )
        pos = self.mapToGlobal(self.rect().bottomRight())
        dlg.move(pos.x() - dlg.sizeHint().width() - 10, pos.y() - 130)
        dlg.exec()

    def set_accent(self, color):
        self.accent = color
        self.data["accent"] = color
        datastore.save(self.data)
        self.build_ui()

    def set_bg(self, color):
        self.bg = color
        self.theme = theme_for(color)
        self.data["bg"] = color
        datastore.save(self.data)
        self.apply_bg()
        self.build_ui()

    def check_two_col(self):
        at_max = self.height() >= self.maximumHeight()
        if at_max != self._at_max_height:
            self._at_max_height = at_max
            for w in self.cat_widgets:
                w.set_two_col(at_max)

    def position_top_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 20, screen.top() + 20)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.check_two_col()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def focusOutEvent(self, e):
        self.hide()