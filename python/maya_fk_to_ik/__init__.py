import maya.OpenMayaUI as omui  # noqa: N813 # type: ignore
import shiboken6
from PySide6 import QtWidgets

from .gui.gui import MatchFKToIKGUI


def _get_maya_main_window() -> QtWidgets.QWidget:
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken6.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)  # type: ignore


def show() -> None:
    """MatchFKToIKGUIを表示する"""
    gui = MatchFKToIKGUI(_get_maya_main_window())
    gui.show()
