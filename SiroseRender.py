import os
import sys
import configparser
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QTabWidget, QMainWindow, QPushButton, QToolBar, QDialog, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QMessageBox, QSizePolicy, QWidget
from PyQt5.QtGui import QIcon

from maya_arnold_widget import MayaArnoldWidget
from husk_karma_widget import HuskKarmaWidget

HISTORY_PATH = "render_history.json"


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des rendus")
        self.setGeometry(400, 400, 500, 400)
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(QLabel("Rendus précédents :"))
        layout.addWidget(self.list_widget)
        self.reload_history()
        self.setLayout(layout)

    def reload_history(self):
        self.list_widget.clear()
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        date = entry.get("date", "")
                        scene = entry.get("scene", "")
                        status = entry.get("status", "")
                        duration = entry.get("duration", "")
                        self.list_widget.addItem(
                            f"{date} | {scene} | {status} | {duration}")
                    except Exception:
                        continue


def add_toolbar_spacer(toolbar, width=8):
    spacer = QWidget()
    spacer.setFixedWidth(width)
    spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    toolbar.addWidget(spacer)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiroseRender")
        icon_path = os.path.join(
            getattr(sys, '_MEIPASS', os.path.dirname(
                os.path.abspath(__file__))),
            "icon.ico"
        )
        self.setWindowIcon(QIcon(icon_path))

        # Gestion du thème sauvegardé et des chemins d'environnement
        self.config_path = "config.ini"
        self.config = configparser.ConfigParser()

        # S'assurer que le fichier de config existe avec les sections nécessaires
        self.initialize_config()

        # Charger les chemins d'environnement avant la création des widgets
        self.load_environment_paths()

        toolbar = QToolBar("Theme")
        self.addToolBar(toolbar)

        # Spacer expansif pour pousser tout à droite
        right_spacer = QWidget()
        right_spacer.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(right_spacer)

        # Bouton clear
        self.clear_fields_button = QPushButton()
        self.clear_icon = QIcon(os.path.join(
            os.path.dirname(__file__), "clear.png"))
        self.clear_fields_button.setIcon(self.clear_icon)
        self.clear_fields_button.setToolTip(
            "Effacer tous les champs de l'onglet ouvert")
        self.clear_fields_button.clicked.connect(self.clear_current_tab_fields)
        toolbar.addWidget(self.clear_fields_button)

        add_toolbar_spacer(toolbar, 8)

        # Bouton historique
        self.history_button = QPushButton()
        self.history_icon = QIcon(os.path.join(
            os.path.dirname(__file__), "history.png"))
        self.history_button.setIcon(self.history_icon)
        self.history_button.setToolTip("Afficher l'historique des rendus")
        self.history_button.clicked.connect(self.open_history)
        toolbar.addWidget(self.history_button)

        add_toolbar_spacer(toolbar, 8)

        # Bouton thème
        self.theme_button = QPushButton()
        self.sun_icon = QIcon(os.path.join(
            os.path.dirname(__file__), "sun.png"))
        self.moon_icon = QIcon(os.path.join(
            os.path.dirname(__file__), "moon.png"))
        self.theme_button.setToolTip("Basculer Light/Dark mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_button)

        # Onglets
        self.tabs = QTabWidget()
        self.maya_widget = MayaArnoldWidget(self.config_path)
        self.husk_widget = HuskKarmaWidget(self.config_path)
        self.tabs.addTab(self.maya_widget, "Maya/Arnold")
        self.tabs.addTab(self.husk_widget, "Houdini/Karma")
        self.setCentralWidget(self.tabs)
        self.setGeometry(200, 200, 600, 600)

        # Appliquer le thème au démarrage
        self.apply_theme()

    def initialize_config(self):
        self.config.read(self.config_path)

        # S'assurer que la section Theme existe
        if not self.config.has_section("Theme"):
            self.config.add_section("Theme")
            self.config.set("Theme", "mode", "light")

        # S'assurer que la section Paths existe avec les valeurs par défaut
        if not self.config.has_section("Paths"):
            self.config.add_section("Paths")
            self.config.set("Paths", "MAYA_PATH",
                            "C:\\Program Files\\Autodesk\\Maya2024\\bin")
            self.config.set("Paths", "QT_PLUGIN_PATH",
                            "C:\\Program Files\\Autodesk\\Maya2024\\plugins")
            self.config.set("Paths", "HOUDINI_BIN",
                            "C:\\Program Files\\Side Effects Software\\Houdini 20.5.487\\bin")

        # Sauvegarder la configuration
        with open(self.config_path, "w") as configfile:
            self.config.write(configfile)

        # Relire la configuration après l'avoir écrite
        self.config.read(self.config_path)
        self.theme_mode = self.config.get("Theme", "mode", fallback="light")

    def load_environment_paths(self):
        """Charge tous les chemins d'environnement nécessaires pour les renderers"""
        # Chemins Maya
        maya_path = self.config.get("Paths", "MAYA_PATH",
                                    fallback="C:\\Program Files\\Autodesk\\Maya2024\\bin")
        qt_plugin_path = self.config.get("Paths", "QT_PLUGIN_PATH",
                                         fallback="C:\\Program Files\\Autodesk\\Maya2024\\plugins")

        # Chemin Houdini
        houdini_bin = self.config.get("Paths", "HOUDINI_BIN",
                                      fallback="C:\\Program Files\\Side Effects Software\\Houdini 20.5.487\\bin")

        # Configuration Maya/Arnold
        if os.path.exists(maya_path):
            os.environ["PATH"] = maya_path + ";" + os.environ["PATH"]

        if os.path.exists(qt_plugin_path):
            os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

        # Configuration Arnold
        arnold_root = "C:\\Program Files\\Autodesk\\Arnold\\maya2024"
        arnold_plugin = arnold_root + "\\plug-ins"
        arnold_bin = arnold_root + "\\bin"
        arnold_python = arnold_root + "\\scripts"

        if os.path.exists(arnold_bin):
            os.environ["PATH"] = arnold_bin + ";" + os.environ["PATH"]

        if os.path.exists(arnold_plugin):
            if "MAYA_PLUG_IN_PATH" in os.environ:
                os.environ["MAYA_PLUG_IN_PATH"] = arnold_plugin + \
                    ";" + os.environ["MAYA_PLUG_IN_PATH"]
            else:
                os.environ["MAYA_PLUG_IN_PATH"] = arnold_plugin

        if os.path.exists(arnold_python):
            if "PYTHONPATH" in os.environ:
                os.environ["PYTHONPATH"] = arnold_python + \
                    ";" + os.environ["PYTHONPATH"]
            else:
                os.environ["PYTHONPATH"] = arnold_python

        # Configuration Houdini
        if os.path.exists(houdini_bin):
            os.environ["PATH"] = houdini_bin + ";" + os.environ["PATH"]

    def open_history(self):
        dlg = HistoryDialog(self)
        dlg.exec_()

    def apply_theme(self):
        if self.theme_mode == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #232629;
                    color: #f0f0f0;
                }
                QPushButton, QLineEdit, QTextEdit, QListWidget {
                    background-color: #31363b;
                    color: #f0f0f0;
                }
                QTabWidget::pane {
                    background: #232629;
                }
                QTabBar::tab {
                    background: #31363b;
                    color: #f0f0f0;
                    padding: 8px;
                    border: 1px solid #232629;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background: #232629;
                    color: #ffcc00;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """)
            self.theme_button.setIcon(self.sun_icon)
        else:
            self.setStyleSheet("")
            self.theme_button.setIcon(self.moon_icon)

    def toggle_theme(self):
        if self.theme_mode == "light":
            self.theme_mode = "dark"
        else:
            self.theme_mode = "light"
        self.apply_theme()
        # Sauvegarde dans le fichier de config
        if not self.config.has_section("Theme"):
            self.config.add_section("Theme")
        self.config.set("Theme", "mode", self.theme_mode)
        with open(self.config_path, "w") as configfile:
            self.config.write(configfile)

    def clear_current_tab_fields(self):
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "clear_fields"):
            current_widget.clear_fields()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(
        getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),
        "icon.ico"
    )
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
