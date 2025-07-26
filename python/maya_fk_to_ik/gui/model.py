from __future__ import annotations

from enum import Enum
from typing import Any

import maya.cmds as cmds  # type: ignore
from PySide6 import QtCore

from ..core.match_info import MatchInfo, MatchInfos
from ..core.rotate_type import RotateType

HEADER_FK_CTRL = "FK Controller"
HEADER_JOINT = "Joint"
HEADER_ROTATE_TYPE = "Rotate Type"
HEADERS = [HEADER_FK_CTRL, HEADER_JOINT, HEADER_ROTATE_TYPE]


class UserRole(int, Enum):
    """カスタムデータロール"""
    MatchInfo = QtCore.Qt.ItemDataRole.UserRole + 1


class MatchInfoTableModel(QtCore.QAbstractTableModel):
    """FKコントローラーとジョイントのマッチ情報を表示するテーブルモデル"""
    def __init__(self, match_infos: MatchInfos, parent=None) -> None:
        super().__init__(parent)
        self.match_infos = match_infos
        self.headers = HEADERS

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:  # type: ignore
        return len(self.match_infos)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:  # type: ignore
        return len(self.headers)

    def setData(self, index: QtCore.QModelIndex, value: Any, role=QtCore.Qt.ItemDataRole.EditRole) -> bool:  # type: ignore
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.EditRole:
            return False
        if index.column() == HEADERS.index(HEADER_ROTATE_TYPE):
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
            if index.column() == HEADERS.index(HEADER_FK_CTRL):
                return get_simple_node_name(match_info.fk_ctrl)
            if index.column() == HEADERS.index(HEADER_JOINT):
                return get_simple_node_name(match_info.joint)
            if index.column() == HEADERS.index(HEADER_ROTATE_TYPE):
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

def undo() -> None:
    """MayaのUndoを実行する"""
    cmds.undo()  # type: ignore
