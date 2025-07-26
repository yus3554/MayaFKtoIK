from pathlib import Path
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from ..app import MatchFKToIK
from ..core.const import DEFAULT_MATCH_INFO_FILE_NAME, DEFAULT_SETTINGS_FOLDER_PATH
from .model import (
    MatchInfoTableModel,
    RotateTypeDelegate,
    UserRole,
    get_match_info_from_selection,
    select_node,
)
from .ui.main_ui import Ui_MainWindow

if TYPE_CHECKING:
    from ..core.match_info import MatchInfo

GUI_SETTINGS_FILE = DEFAULT_SETTINGS_FOLDER_PATH / "gui_settings.ini"


class MatchFKToIKGUI(QtWidgets.QMainWindow):
    """Match FK to IKのGUIクラス"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # GUIの初期化
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Match FK to IK")

        # MatchFKToIKのインスタンスを作成
        self.match_fk_to_ik = MatchFKToIK()

        # 初期設定ファイルからマッチ情報を読み込む
        if not DEFAULT_SETTINGS_FOLDER_PATH.exists():
            DEFAULT_SETTINGS_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
        if (DEFAULT_SETTINGS_FOLDER_PATH / DEFAULT_MATCH_INFO_FILE_NAME).exists():
            self.match_fk_to_ik.match_infos.load_json(DEFAULT_SETTINGS_FOLDER_PATH / DEFAULT_MATCH_INFO_FILE_NAME)

        # テーブルビューの設定
        self.ui.match_info_table_view.setModel(MatchInfoTableModel(self.match_fk_to_ik.match_infos))
        self.ui.match_info_table_view.setItemDelegateForColumn(2, RotateTypeDelegate(self.ui.match_info_table_view))
        self.ui.match_info_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.match_info_table_view.horizontalHeader().setStretchLastSection(True)
        self.ui.match_info_table_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.match_info_table_view.customContextMenuRequested.connect(self._open_table_menu)
        self.ui.match_info_table_view.doubleClicked.connect(self._on_double_click_table)
        # TODO: 回転タイプを選択できるようにする（回転タイプの選択肢をGUIで提供する）これは、クリックしている間は回転タイプが適用された状態がビューに表示され、離したら戻るようにして決めてもらう
        # TODO: 今はコンボボックスで選択するようにしているが、クリックしている間は回転タイプが適用された状態がビューに表示され、離したら戻るようにして決めてもらう

        # シグナルとスロットの接続
        self.ui.match_button.clicked.connect(self.match_fk_to_ik_controller)
        self.ui.add_button.clicked.connect(self.add_match_info)

        # GUIの設定を復元
        self.restore(GUI_SETTINGS_FILE)

    def match_fk_to_ik_controller(self) -> None:
        """FKコントローラーの回転をIKジョイントに合わせる"""
        # テーブルの選択された行のFKコントローラーを取得
        selected_indexes = self.ui.match_info_table_view.selectedIndexes()

        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "選択エラー", "マッチ情報を選択してください。")
            return

        for index in selected_indexes:
            if not index.isValid():
                continue

            match_info: MatchInfo = self.ui.match_info_table_view.model().data(index, UserRole.MatchInfo)
            if not match_info:
                QtWidgets.QMessageBox.warning(self, "選択エラー", "マッチ情報が見つかりません。")
                return

            if match_info:
                self.match_fk_to_ik.match(match_info.fk_ctrl)
                self.ui.match_info_table_view.model().layoutChanged.emit()
            else:
                QtWidgets.QMessageBox.warning(self, "入力エラー", "FKコントローラー名を入力してください。")

    def add_match_info(self) -> None:
        """マッチ情報を追加する"""
        match_info = get_match_info_from_selection()
        if not match_info:
            QtWidgets.QMessageBox.warning(self, "選択エラー", "FKコントローラーとジョイントを選択してください。")
            return

        fk_ctrl = match_info.fk_ctrl
        joint = match_info.joint
        rotate_type = match_info.type

        if fk_ctrl and joint and rotate_type:
            self.match_fk_to_ik.match_infos.add(joint=joint, fk_ctrl=fk_ctrl, rotate_type=rotate_type)
            self.ui.match_info_table_view.model().layoutChanged.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "入力エラー", "すべてのフィールドに入力してください。")

    def _open_table_menu(self, position: QtCore.QPoint) -> None:
        """テーブルのコンテキストメニューを開く"""
        menu = QtWidgets.QMenu(self.ui.match_info_table_view)

        remove_action = menu.addAction("Remove")
        remove_action.triggered.connect(self._remove_match_info)

        menu.exec_(self.ui.match_info_table_view.viewport().mapToGlobal(position))

    def _remove_match_info(self) -> None:
        """選択されたマッチ情報を削除する"""
        selected_index = self.ui.match_info_table_view.currentIndex()
        if not selected_index.isValid():
            QtWidgets.QMessageBox.warning(self, "選択エラー", "削除する行を選択してください。")
            return

        match_info = self.ui.match_info_table_view.model().data(selected_index, UserRole.MatchInfo)
        if not match_info:
            QtWidgets.QMessageBox.warning(self, "選択エラー", "削除するマッチ情報が見つかりません。")
            return
        self.match_fk_to_ik.match_infos.remove(match_info.fk_ctrl)
        self.ui.match_info_table_view.model().layoutChanged.emit()
        QtWidgets.QMessageBox.information(self, "削除完了", "マッチ情報が削除されました。")

    def _on_double_click_table(self, index: QtCore.QModelIndex) -> None:
        """テーブルのダブルクリックイベントハンドラ"""
        if not index.isValid():
            return

        if index.column() == 0:  # FKコントローラーの列
            self._select_fk_controller()
        elif index.column() == 1:  # ジョイントの列
            self._select_joint()

    def _select_fk_controller(self) -> None:
        """選択されたFKコントローラーを選択する"""
        selected_index = self.ui.match_info_table_view.currentIndex()
        if not selected_index.isValid():
            QtWidgets.QMessageBox.warning(self, "選択エラー", "FKコントローラーを選択してください。")
            return

        match_info = self.ui.match_info_table_view.model().data(selected_index, UserRole.MatchInfo)
        if match_info:
            select_node(match_info.fk_ctrl)

    def _select_joint(self) -> None:
        """選択されたジョイントを選択する"""
        selected_index = self.ui.match_info_table_view.currentIndex()
        if not selected_index.isValid():
            QtWidgets.QMessageBox.warning(self, "選択エラー", "ジョイントを選択してください。")
            return

        match_info = self.ui.match_info_table_view.model().data(selected_index, UserRole.MatchInfo)
        if match_info:
            select_node(match_info.joint)

    def restore(self, settings_file: Path) -> None:
        """GUIの設定を復元する"""
        if not settings_file.exists():
            return

        settings = QtCore.QSettings(str(settings_file), QtCore.QSettings.Format.IniFormat)
        self.restoreGeometry(settings.value("geometry", QtCore.QByteArray()))  # type: ignore
        self.restoreState(settings.value("windowState", QtCore.QByteArray()))  # type: ignore

        table_geometry = settings.value("tableGeometry", QtCore.QByteArray())
        if table_geometry:
            self.ui.match_info_table_view.horizontalHeader().restoreGeometry(table_geometry)  # type: ignore
        table_state = settings.value("tableState", QtCore.QByteArray())
        if table_state:
            self.ui.match_info_table_view.horizontalHeader().restoreState(table_state)  # type: ignore

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """ウィンドウを閉じるときの処理"""
        self.match_fk_to_ik.match_infos.export_json(DEFAULT_SETTINGS_FOLDER_PATH / DEFAULT_MATCH_INFO_FILE_NAME)

        settings = QtCore.QSettings(str(GUI_SETTINGS_FILE), QtCore.QSettings.Format.IniFormat)
        settings.setValue("geometry", self.saveGeometry())  # type: ignore
        settings.setValue("windowState", self.saveState())
        settings.setValue("tableGeometry", self.ui.match_info_table_view.horizontalHeader().saveGeometry())
        settings.setValue("tableState", self.ui.match_info_table_view.horizontalHeader().saveState())
        settings.sync()
        event.accept()
