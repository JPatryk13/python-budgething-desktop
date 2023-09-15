import sys
from typing import Any

from PyQt6 import QtWidgets, QtCore, QtGui

from budgeting_app.gui.services.base import MainWindow
from budgeting_app.gui.utils.tools import create_text_area_with_label


class AddProfileForm(MainWindow):

    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.setWindowTitle("Budgeting App - Select Profile")
        
        self.window_width, self.window_height = 400, 500
        self.setFixedSize(self.window_width, self.window_height)
        
        # Create a central widget and layout to hold the profile form
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
        self._create_form_header()
        self._create_new_profile_form()
        self._create_form_footer()
        
    def _create_form_header(self) -> None:
        # Create form header
        form_label = QtWidgets.QLabel('New Profile')
        form_label_font = QtGui.QFont()
        form_label_font.setPointSize(14)
        form_label.setFont(form_label_font)
        self.main_layout.addWidget(form_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        
        # Line separating form header and the form
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.main_layout.addWidget(line)
    
    def _create_new_profile_form(self) -> None:
        # Name field
        self.name_widget, self.name_text_area = create_text_area_with_label('Name*', 'top')
        self.main_layout.addWidget(self.name_widget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Password field
        self.password_widget, self.password_text_area = create_text_area_with_label('Password', 'top', _echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.main_layout.addWidget(self.password_widget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Confirm password field
        self.password_widget, self.password_text_area = create_text_area_with_label('Confirm password', 'top', _echo_mode=QtWidgets.QLineEdit.EchoMode.Password)
        self.main_layout.addWidget(self.password_widget, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Form submit button
        self.submit_button = QtWidgets.QPushButton('Submit')
        self.submit_button.clicked.connect(self.__submit_profile_data)
        self.main_layout.addWidget(self.submit_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # I don't remember what it does but the form looks better with it
        self.main_layout.addStretch()
        
    def _create_form_footer(self) -> None:
        # Add footer frame
        footer = QtWidgets.QFrame(self)
        footer.setMinimumHeight(50)
        
        # That's a nice shade of gray
        footer.setStyleSheet("background-color: #dadada;")
        
        footer_layout = QtWidgets.QVBoxLayout()
        footer.setLayout(footer_layout)
        
        footer_content = QtWidgets.QLabel('*Required fields')
        footer_content.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(footer_content)
        self.main_layout.addWidget(footer)
        
    def __submit_profile_data(self) -> None:
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    select_profile = AddProfileForm()
    select_profile.show()
    sys.exit(app.exec())