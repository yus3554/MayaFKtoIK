from PySide6 import QtWidgets

from match_fk_to_ik.scripts.app import MatchFKToIK

from .ui.main_ui import Ui_MainWindow


class MatchFKToIKGUI(Ui_MainWindow, QtWidgets.QMainWindow):
    """GUI for matching FK controllers to IK joints"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Match FK to IK")
        self.match_fk_to_ik = MatchFKToIK()

        # GUI components setup can be added here
        # For example, buttons, labels, input fields, etc.
        # self.setup_ui()

    # Additional methods for GUI functionality can be added here
    # def setup_ui(self):
    #     pass
