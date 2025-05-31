import os
import configparser
import subprocess
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QRadioButton, QButtonGroup, QTextEdit, QFormLayout, QStatusBar, QGroupBox,
                             QDialog, QListWidget, QMessageBox)
from datetime import datetime
import json

HISTORY_PATH = "render_history.json"


class SettingsDialog(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres Maya/Arnold")
        self.setGeometry(300, 300, 500, 150)
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        maya_path = self.config.get(
            "Paths", "MAYA_PATH", fallback="C:\\Program Files\\Autodesk\\Maya2024\\bin")
        qt_plugin_path = self.config.get(
            "Paths", "QT_PLUGIN_PATH", fallback="C:\\Program Files\\Autodesk\\Maya2024\\plugins")

        layout = QFormLayout()
        self.maya_path_input = QLineEdit(maya_path)
        browse_maya = QPushButton("Parcourir")
        browse_maya.clicked.connect(self.browse_maya_path)
        maya_layout = QHBoxLayout()
        maya_layout.addWidget(self.maya_path_input)
        maya_layout.addWidget(browse_maya)
        layout.addRow("Chemin Maya bin :", maya_layout)

        self.qt_plugin_path_input = QLineEdit(qt_plugin_path)
        browse_qt = QPushButton("Parcourir")
        browse_qt.clicked.connect(self.browse_qt_plugin_path)
        qt_layout = QHBoxLayout()
        qt_layout.addWidget(self.qt_plugin_path_input)
        qt_layout.addWidget(browse_qt)
        layout.addRow("Chemin Qt plugins :", qt_layout)

        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)

        self.setLayout(layout)

    def browse_maya_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier Maya bin")
        if folder:
            self.maya_path_input.setText(folder)

    def browse_qt_plugin_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier Qt plugins")
        if folder:
            self.qt_plugin_path_input.setText(folder)

    def save_settings(self):
        if not self.config.has_section("Paths"):
            self.config.add_section("Paths")
        self.config.set("Paths", "MAYA_PATH", self.maya_path_input.text())
        self.config.set("Paths", "QT_PLUGIN_PATH",
                        self.qt_plugin_path_input.text())
        with open(self.config_path, "w") as config_file:
            self.config.write(config_file)

        # Demander à la fenêtre principale de recharger les chemins
        self.parent().parent().load_environment_paths()
        self.accept()


class DraggableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.setText(file_path)


class MayaArnoldWidget(QWidget):
    def __init__(self, config_path=None):
        super().__init__()
        self.setWindowTitle('Automatisation de Rendus Maya/Arnold')
        self.config_path = config_path or "config.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self.render_queue = []

        main_layout = QVBoxLayout()
        self.create_form_layout(main_layout)
        self.create_render_queue_section(main_layout)
        self.create_log_section(main_layout)

        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage('Prêt à lancer le rendu.')
        main_layout.addWidget(self.status_bar)

        launch_button = QPushButton("Lancer")
        launch_button.clicked.connect(self.start_render)
        main_layout.addWidget(launch_button)

        settings_button = QPushButton("Paramètres")
        settings_button.clicked.connect(self.open_settings_dialog)
        main_layout.addWidget(settings_button)

        self.setLayout(main_layout)

    def load_environment_paths(self):
        maya_path = self.config.get(
            "Paths", "MAYA_PATH", fallback="C:\\Program Files\\Autodesk\\Maya2024\\bin")
        qt_plugin_path = self.config.get(
            "Paths", "QT_PLUGIN_PATH", fallback="C:\\Program Files\\Autodesk\\Maya2024\\plugins")

        os.environ["PATH"] = maya_path + ";" + os.environ["PATH"]
        os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

        # Ajoute ces lignes pour Arnold
        arnold_root = "C:\\Program Files\\Autodesk\\Arnold\\maya2024"
        arnold_plugin = arnold_root + "\\plug-ins"
        arnold_bin = arnold_root + "\\bin"
        arnold_python = arnold_root + "\\scripts"

        # Ajoute Arnold au PATH
        os.environ["PATH"] = arnold_bin + ";" + os.environ["PATH"]

        # Ajoute le chemin des plugins Arnold
        if "MAYA_PLUG_IN_PATH" in os.environ:
            os.environ["MAYA_PLUG_IN_PATH"] = arnold_plugin + \
                ";" + os.environ["MAYA_PLUG_IN_PATH"]
        else:
            os.environ["MAYA_PLUG_IN_PATH"] = arnold_plugin

        # Ajoute le chemin des scripts Python Arnold
        if "PYTHONPATH" in os.environ:
            os.environ["PYTHONPATH"] = arnold_python + \
                ";" + os.environ["PYTHONPATH"]
        else:
            os.environ["PYTHONPATH"] = arnold_python

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.config_path, self)
        dialog.exec_()

    def create_form_layout(self, layout):
        form_layout = QFormLayout()

        self.scene_path_input = DraggableLineEdit(self)
        browse_button = QPushButton("Parcourir", self)
        browse_button.clicked.connect(self.open_file_dialog)
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self.scene_path_input)
        browse_layout.addWidget(browse_button)
        form_layout.addRow('Chemin de la scène Maya :', browse_layout)

        self.output_dir_input = QLineEdit(self)
        browse_output = QPushButton("Parcourir", self)
        browse_output.clicked.connect(self.open_folder_dialog)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(browse_output)
        form_layout.addRow('Dossier de sortie :', output_layout)

        self.start_frame_input = QLineEdit(self)
        form_layout.addRow('Frame de début :', self.start_frame_input)

        self.end_frame_input = QLineEdit(self)
        form_layout.addRow('Frame de fin :', self.end_frame_input)

        self.resolution_input = QLineEdit(self)
        form_layout.addRow('Résolution en pourcentage :',
                           self.resolution_input)

        self.render_layer_input = QLineEdit(self)
        form_layout.addRow('Render Layer (optionnel) :',
                           self.render_layer_input)

        render_type_group = QGroupBox("Type de rendu")
        render_type_layout = QHBoxLayout()
        self.full_render_radio = QRadioButton("Full Sequence", self)
        self.fml_render_radio = QRadioButton("FML", self)
        self.full_render_radio.setChecked(True)
        render_type_layout.addWidget(self.full_render_radio)
        render_type_layout.addWidget(self.fml_render_radio)
        render_type_group.setLayout(render_type_layout)
        form_layout.addRow(render_type_group)

        add_render_button = QPushButton("Ajouter à la file d'attente")
        add_render_button.clicked.connect(self.add_render_to_queue)
        form_layout.addRow(add_render_button)

        layout.addLayout(form_layout)

    def create_render_queue_section(self, layout):
        self.render_queue_list = QListWidget(self)
        layout.addWidget(QLabel("File d'attente des rendus :"))
        layout.addWidget(self.render_queue_list)

        remove_button = QPushButton("Supprimer le rendu sélectionné")
        remove_button.clicked.connect(self.remove_selected_render)
        layout.addWidget(remove_button)

    def create_log_section(self, layout):
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir la scène Maya", "", "Fichiers Maya (*.ma *.mb)")
        if filename:
            self.scene_path_input.setText(filename)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choisir le dossier de sortie")
        if folder:
            self.output_dir_input.setText(folder)

    def log_message(self, message):
        self.log_text.append(message)
        self.status_bar.showMessage(message)

    def add_render_to_queue(self):
        scene_path = self.scene_path_input.text()
        output_dir = self.output_dir_input.text()
        start_frame = self.start_frame_input.text()
        end_frame = self.end_frame_input.text()
        resolution = self.resolution_input.text()
        render_layer = self.render_layer_input.text()
        render_type = "full" if self.full_render_radio.isChecked() else "fml"

        if not scene_path or not output_dir or not start_frame or not end_frame or not resolution:
            QMessageBox.warning(
                self, "Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            start_frame_int = int(start_frame)
            end_frame_int = int(end_frame)
            res_scale_int = int(resolution)
        except ValueError:
            QMessageBox.warning(
                self, "Erreur", "Les frames et la résolution doivent être des entiers.")
            return

        render_job = {
            "scene_path": scene_path,
            "output_dir": output_dir,
            "start_frame": start_frame_int,
            "end_frame": end_frame_int,
            "render_layer": render_layer if render_layer else None,
            "res_scale": res_scale_int,
            "render_type": render_type
        }

        # Génération de la preview de la ou des commandes (ordre correct des arguments)
        base_cmd = f'render -r arnold -rd "{output_dir}" -fnc name_#.ext -percentRes {res_scale_int}'
        if render_layer:
            base_cmd += f' -rl {render_layer}'

        if render_type == "full":
            cmd_preview = f'{base_cmd} -s {start_frame_int} -e {end_frame_int} "{scene_path}"'
        else:
            mid_frame = start_frame_int + \
                ((end_frame_int - start_frame_int) // 2)
            frames = [start_frame_int, mid_frame, end_frame_int]
            cmd_preview = "\n".join(
                f'{base_cmd} -s {frame} -e {frame} "{scene_path}"' for frame in frames
            )

        self.render_queue.append(render_job)
        self.render_queue_list.addItem(cmd_preview)
        self.log_message(f"Ajouté à la file :\n{cmd_preview}")

    def remove_selected_render(self):
        selected = self.render_queue_list.currentRow()
        if selected >= 0:
            self.render_queue_list.takeItem(selected)
            del self.render_queue[selected]
            self.log_message("Rendu supprimé de la file.")

    def start_render(self):
        if not self.render_queue:
            QMessageBox.information(
                self, "Info", "La file d'attente est vide.")
            return
        self.start_render_queue()

    def start_render_queue(self):
        total = len(self.render_queue)
        for idx, render in enumerate(self.render_queue):
            if render["render_type"] == "full":
                self.render_scene_full(
                    render["scene_path"],
                    render["start_frame"],
                    render["end_frame"],
                    render["output_dir"],
                    render["render_layer"],
                    render["res_scale"]
                )
            else:
                self.render_scene_fml(
                    render["scene_path"],
                    render["start_frame"],
                    render["end_frame"],
                    render["output_dir"],
                    render["render_layer"],
                    render["res_scale"]
                )
        self.log_message("Tous les rendus de la file ont été lancés.")

    def render_scene_full(self, scene_path, start_frame, end_frame, output_dir, render_layer=None, percent_res=100):
        self.log_message(
            f"\n=== Lancement du rendu complet pour la scène : {scene_path} ===")
        cmd = f'render -r arnold -s {start_frame} -e {end_frame} -rd {output_dir} -fnc name_#.ext -percentRes {percent_res}'
        if render_layer:
            cmd += f' -rl {render_layer}'
        cmd += f' "{scene_path}"'
        self.log_message(f"Commande de rendu : {cmd}")
        subprocess.run(cmd, shell=True)
        self.log_message("\n=== Rendu complet terminé. ===")

    def render_scene_fml(self, scene_path, start_frame, end_frame, output_dir, render_layer=None, percent_res=100):
        self.log_message(
            f"\n=== Lancement du rendu rapide (FML) pour la scène : {scene_path} ===")
        total_frames = end_frame - start_frame + 1
        mid_frame = start_frame + (total_frames // 2)
        frames = [start_frame, mid_frame, end_frame]
        for frame in frames:
            cmd = f'render -r arnold -s {frame} -e {frame} -rd {output_dir} -fnc name_#.ext -percentRes {percent_res}'
            if render_layer:
                cmd += f' -rl {render_layer}'
            cmd += f' "{scene_path}"'
            self.log_message(f"Commande de rendu pour frame {frame} : {cmd}")
            subprocess.run(cmd, shell=True)
        self.log_message("\n=== Rendu rapide (FML) terminé. ===")

    # À la fin d'un rendu (succès ou échec)
    def add_to_history(self, scene, status, duration):
        entry = {
            "scene": scene,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "duration": duration
        }
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def clear_fields(self):
        self.scene_path_input.clear()
        self.output_dir_input.clear()
        self.start_frame_input.clear()
        self.end_frame_input.clear()
        self.render_layer_input.clear()
        self.resolution_input.clear()
        self.output_dir_input.clear()
        self.full_render_radio.setChecked(True)
        self.render_queue.clear()
        self.render_queue_list.clear()
        self.log_text.clear()
