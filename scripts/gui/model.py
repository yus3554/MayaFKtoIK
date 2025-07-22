from __future__ import annotations

from typing import Any

from PySide6 import QtCore


class MatchInfoTableModel(QtCore.QAbstractTableModel):
    """FKコントローラーとIKジョイントのマッチ情報を表示するテーブルモデル"""
    def __init__(self, match_infos_manager, parent=None) -> None:
        super().__init__(parent)
        self.match_infos_manager = match_infos_manager
        self.headers = ["Character Name", "FK Controller", "IK Joint", "Rotate Type"]

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:  # noqa: ARG002, B008, D102, N802 # type: ignore
        return sum(len(info) for info in self.match_infos_manager.match_infos_dict.values())

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:  # noqa: ARG002, B008, D102, N802 # type: ignore
        return len(self.headers)

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole) -> Any | None:  # noqa: ANN401, D102 # type: ignore
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        character_name = list(self.match_infos_manager.match_infos_dict.keys())[index.row()]
        match_info = list(self.match_infos_manager.match_infos_dict[character_name].values())[index.column()]

        if index.column() == 0:
            return character_name
        if index.column() == 1:
            return match_info.fk_ctrl
        if index.column() == 2:  # noqa: PLR2004
            return match_info.ik_joint
        if index.column() == 3:  # noqa: PLR2004
            return match_info.type.name
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole) -> Any | None:  # noqa: ANN401, D102, N802  # type: ignore
        if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self.headers[section]
        return None
