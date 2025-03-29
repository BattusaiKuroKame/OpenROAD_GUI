import sys
import os
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt

class PDKManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDK Manager")
        self.setGeometry(100, 100, 600, 500)
        self.initUI()
        self.current_file = None
        self.imported_design = None  # Store the last imported design name
    
    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Create a splitter for dynamic resizing
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Console Output (Left Side, takes most space)
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        splitter.addWidget(self.console_output)
        
        # Buttons Layout (Right Side, Snapped to Top)
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Select PDK (Same row as dropdown)
        pdk_layout = QHBoxLayout()
        self.pdk_label = QLabel("Select PDK:")
        self.pdk_dropdown = QComboBox()
        self.populate_pdk_dropdown()
        self.pdk_dropdown.currentTextChanged.connect(self.pdk_changed)
        pdk_layout.addWidget(self.pdk_label)
        pdk_layout.addWidget(self.pdk_dropdown)
        buttons_layout.addLayout(pdk_layout)
        
        # Imported Design Label
        self.imported_design_label = QLabel("Imported Design: None")
        buttons_layout.addWidget(self.imported_design_label)
        
        # Import Design
        self.import_design_button = QPushButton("Import Design")
        self.import_design_button.clicked.connect(self.import_design)
        buttons_layout.addWidget(self.import_design_button)
        
        # Edit config.mk & Reset config.mk (Same Row)
        config_layout = QHBoxLayout()
        self.edit_config_button = QPushButton("Edit config.mk")
        self.edit_config_button.clicked.connect(lambda: self.edit_file("config.mk"))
        config_layout.addWidget(self.edit_config_button)
        
        self.reset_config_button = QPushButton("Reset config.mk")
        self.reset_config_button.clicked.connect(self.reset_config)
        config_layout.addWidget(self.reset_config_button)
        buttons_layout.addLayout(config_layout)
        
        # Edit constraints.sdk & Reset constraints.sdk (Same Row)
        constraints_layout = QHBoxLayout()
        self.edit_constraints_button = QPushButton("Edit constraints.sdk")
        self.edit_constraints_button.clicked.connect(lambda: self.edit_file("constraints.sdk"))
        constraints_layout.addWidget(self.edit_constraints_button)
        
        self.reset_constraints_button = QPushButton("Reset constraints.sdk")
        self.reset_constraints_button.clicked.connect(self.reset_constraints)
        constraints_layout.addWidget(self.reset_constraints_button)
        buttons_layout.addLayout(constraints_layout)
        
        # Set Makefile & Run Make Layout
        make_layout = QVBoxLayout()
        self.set_makefile_button = QPushButton("Set Makefile")
        self.set_makefile_button.clicked.connect(self.set_makefile)
        make_layout.addWidget(self.set_makefile_button)
        
        self.run_make_button = QPushButton("Run Make")
        self.run_make_button.clicked.connect(self.run_make)
        make_layout.addWidget(self.run_make_button)
        buttons_layout.addLayout(make_layout)
        
        # Edit File Area
        self.text_edit = QTextEdit()
        self.text_edit.setVisible(False)
        buttons_layout.addWidget(self.text_edit)
        
        self.save_button = QPushButton("Save File")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(self.save_button)
        
        # Add button layout to the right side
        splitter.addWidget(buttons_widget)
        
        # Allow resizing
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def log(self, message):
        self.console_output.append(message)
    
    def source_env(self):
        #Windows
        # os.system("source .env")
        # self.log("Sourced .env file")

        #Ubuntu
        # Run the 'source .env' command in a new bash process and execute additional commands if necessary
        result = subprocess.run(["bash", "-i", "-c", "source .env && echo 'Env sourced'"], capture_output=True, text=True)
        if result.returncode == 0:
            self.log(f"Sourced .env file successfully: {result.stdout}")
        else:
            self.log(f"Failed to source .env file: {result.stderr}")
    
    def populate_pdk_dropdown(self):
        pdk_path = "platforms"
        if os.path.exists(pdk_path):
            self.pdk_dropdown.addItems(os.listdir(pdk_path))
    
    def pdk_changed(self, text):
        self.log(f"Selected PDK: {text}")
    
    def import_design(self):
        design_folder = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if design_folder:
            self.imported_design = os.path.basename(design_folder)
            self.imported_design_label.setText(f"Imported Design: {self.imported_design}")
            selected_pdk = self.pdk_dropdown.currentText()
            dest_src = f"designs/src/{self.imported_design}"
            dest_pdk = f"platforms/{selected_pdk}/{self.imported_design}"
            
            shutil.copytree(design_folder, dest_src, dirs_exist_ok=True)
            shutil.copytree(design_folder, dest_pdk, dirs_exist_ok=True)
            
            shutil.copy("defaultConstraints.txt", f"{dest_pdk}/constraints.sdk")
            shutil.copy("defaultConfig.txt", f"{dest_pdk}/config.mk")
            self.log(f"Imported {self.imported_design} into {dest_pdk} and {dest_src}")
    
    def edit_file(self, file_name):
        selected_pdk = self.pdk_dropdown.currentText()
        file_path = f"platforms/{selected_pdk}/{file_name}"
        if os.path.exists(file_path):
            self.current_file = file_path
            with open(file_path, "r") as file:
                self.text_edit.setText(file.read())
            self.text_edit.setVisible(True)
            self.save_button.setVisible(True)
    
    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_edit.toPlainText())
            self.text_edit.setVisible(False)
            self.save_button.setVisible(False)
            self.log(f"Saved {self.current_file}")
    
    def reset_config(self):
        selected_pdk = self.pdk_dropdown.currentText()
        shutil.copy("defaultConfig.txt", f"platforms/{selected_pdk}/config.mk")
        if self.current_file == f"platforms/{selected_pdk}/config.mk":
            self.edit_file("config.mk")
        self.log("Reset config.mk")
    
    def reset_constraints(self):
        selected_pdk = self.pdk_dropdown.currentText()
        shutil.copy("defaultConstraints.txt", f"platforms/{selected_pdk}/constraints.sdk")
        if self.current_file == f"platforms/{selected_pdk}/constraints.sdk":
            self.edit_file("constraints.sdk")
        self.log("Reset constraints.sdk")
    
    def set_makefile(self):
        if self.imported_design:
            with open("defaultMakefile.txt", "r") as file:
                makefile_data = file.read().replace("nandgate", self.imported_design)
            with open("Makefile", "w") as file:
                file.write(makefile_data)
            self.log("Makefile updated")
        else:
            self.log("No design has been imported yet.")
    
    def run_make(self):
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", "make; exec bash"])
        self.log("Running make...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Dark Mode Style
    dark_stylesheet = """
    QWidget {
        background-color: #2e2e2e;
        color: white;
    }
    QPushButton {
        background-color: #444444;
        color: white;
        border: 1px solid #888888;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    """
    app.setStyleSheet(dark_stylesheet)
    window = PDKManagerApp()
    window.show()
    sys.exit(app.exec())
