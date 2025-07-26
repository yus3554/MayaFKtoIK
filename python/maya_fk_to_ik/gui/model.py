from __future__ import annotations

from enum import Enum
from typing import Any

import maya.cmds as cmds  # type: ignore
from PySide6 import QtCore, QtWidgets

from ..core.match_info import MatchInfo, MatchInfos
from ..core.rotate_type import RotateType


class UserRole(int, Enum):
    """カスタムデータロール"""
    MatchInfo = QtCore.Qt.ItemDataRole.UserRole + 1


class RotateTypeDelegate(QtWidgets.QStyledItemDelegate):
    """RotateTypeのデリゲート"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtWidgets.QComboBox:  # type: ignore
        editor = QtWidgets.QComboBox(parent)
        editor.addItems([rt.name for rt in RotateType])
        return editor

    def setEditorData(self, editor: QtWidgets.QComboBox, index: QtCore.QModelIndex) -> None:  # type: ignore
        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        if value in RotateType.__members__:
            editor.setCurrentText(value)


class MatchInfoTableModel(QtCore.QAbstractTableModel):
    """FKコントローラーとジョイントのマッチ情報を表示するテーブルモデル"""
    def __init__(self, match_infos: MatchInfos, parent=None) -> None:
        super().__init__(parent)
        self.match_infos = match_infos
        self.headers = ["FK Controller", "Joint", "Rotate Type"]

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:  # type: ignore
        return len(self.match_infos)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:  # type: ignore
        return len(self.headers)

    def setData(self, index: QtCore.QModelIndex, value: Any, role=QtCore.Qt.ItemDataRole.EditRole) -> bool:  # type: ignore
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.EditRole:
            return False
        if index.column() == 2:
            # Update the rotate type
            match_info: MatchInfo = list(self.match_infos)[index.row()]
            match_info.type = RotateType[value]
            self.match_infos.edit(match_info.fk_ctrl, match_info)
            return True
        return False

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole) -> Any | None:  # type: ignore
        if not index.isValid():
            return None

        match_info: MatchInfo = list(self.match_infos)[index.row()]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return get_simple_node_name(match_info.fk_ctrl)
            if index.column() == 1:
                return get_simple_node_name(match_info.joint)
            if index.column() == 2:  # noqa: PLR2004
                return match_info.type
        elif role == UserRole.MatchInfo:
            return match_info
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole) -> Any | None:  # type: ignore
        if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:  # type: ignore
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        if index.column() == 2:  # Rotate Type column
            return QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable
        return QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable


def get_simple_node_name(node: str) -> str:
    """ノード名からシンプルな名前を取得する"""
    return cmds.ls(node, shortNames=True)[0] if cmds.objExists(node) else node  # type: ignore


def get_match_info_from_selection() -> MatchInfo | None:
    """現在の選択からマッチ情報を取得する"""
    selection = cmds.ls(selection=True, long=True)  # type: ignore
    if len(selection) < 2:  # noqa: PLR2004
        return None

    fk_ctrl = selection[0]
    joint = selection[1]
    rotate_type = RotateType.FFF  # デフォルトの回転タイプ

    if not cmds.objExists(fk_ctrl):
        cmds.warning(f"FK controller '{fk_ctrl}' does not exist.")
        return None

    if cmds.objectType(joint) != "joint":
        cmds.warning(f"Selected object '{joint}' is not a joint.")
        return None

    return MatchInfo(joint=joint, fk_ctrl=fk_ctrl, type=rotate_type)

def select_node(node: str) -> None:
    """ノードを選択する"""
    if cmds.objExists(node):
        cmds.select(node)
    else:
        cmds.warning(f"Node '{node}' does not exist.")
