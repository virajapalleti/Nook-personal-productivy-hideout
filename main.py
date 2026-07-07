import sys
import threading
import keyboard
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QColor, QPixmap
from PyQt6.QtCore import Qt
from window import NookWindow

def make_tray_icon(accent):
    px = QPixmap(16, 16)
    px.fill(QColor(accent))
    return QIcon(px)

def toggle(window):
    if window.isVisible():
        window.hide()
    else:
        window.show()
        window.position_top_right()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = NookWindow()

    # system tray — not every desktop has one (common on Linux)
    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = QSystemTrayIcon(make_tray_icon(window.accent), app)
        menu = QMenu()
        show_action = menu.addAction("Show Nook")
        quit_action = menu.addAction("Quit")
        show_action.triggered.connect(lambda: toggle(window))
        quit_action.triggered.connect(app.quit)
        tray.setContextMenu(menu)
        tray.activated.connect(lambda reason: toggle(window)
            if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        tray.show()
    else:
        print("Nook: no system tray available — use the hotkey to toggle, "
              "and close the window to quit.", file=sys.stderr)
        # without a tray there is no Quit menu, so let closing the window quit
        app.setQuitOnLastWindowClosed(True)

    # global hotkey in background thread
    def listen():
        try:
            keyboard.add_hotkey("ctrl+shift+space", lambda: toggle(window))
            keyboard.wait()
        except Exception as e:
            # e.g. missing root / 'input' group permissions on Linux —
            # don't die silently, tell the user why the hotkey is dead
            print(f"Nook: global hotkey unavailable ({e}). "
                  "On Linux, add yourself to the 'input' group or run with sudo. "
                  "You can still toggle Nook from the system tray.",
                  file=sys.stderr)

    t = threading.Thread(target=listen, daemon=True)
    t.start()

    window.show()
    window.position_top_right()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()