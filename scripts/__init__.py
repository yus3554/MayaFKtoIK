from .gui.gui import MatchFKToIKGUI


def show() -> None:
    """MatchFKToIKGUIを表示する"""
    gui = MatchFKToIKGUI()
    gui.show()
