from pathlib import Path
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from ..app import MatchFKToIK
from ..core.const import DEFAULT_MATCH_INFO_FILE_NAME, DEFAULT_SETTINGS_FOLDER_PATH
from ..core.rotate_type import RotateType
from .model import (
    HEADER_FK_CTRL,
    HEADER_JOINT,
    HEADER_ROTATE_TYPE,
    HEADERS,
    MatchInfoTableModel,
    UserRole,
    get_match_info_from_selection,
    select_node,
    undo,
)
from .ui.main_ui import Ui_MainWindow

if TYPE_CHECKING:
    from ..core.match_info import MatchInfo

GUI_SETTINGS_FILE = DEFAULT_SETTINGS_FOLDER_PATH / "gui_settings.ini"


class RotateTypeDialog(QtWidgets.QDialog):
    """RotateTypeを選択するダイアログ"""
    pressed_rotate_type_signal = QtCore.Signal(RotateType)
    released_rotate_type_signal = QtCore.Signal()

    def __init__(self, current_rotate_type: RotateType, parent=None) -> None:
        super().__init__(parent)
        self.current_rotate_type = current_rotate_type

        self.setWindowTitle("Select Rotate Type")
        self.resize(300, 200)

        self.layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)  # type: ignore

        self.rotate_type_buttons: list[QtWidgets.QPushButton] = []
        for rotate_type in RotateType:
            button = QtWidgets.QPushButton(rotate_type, self)
            button.pressed.connect(self._on_button_pressed)
            button.released.connect(self._on_button_released)
            self.rotate_type_buttons.append(button)
            self.layout.addWidget(button)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, self)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self._change_all_button_style()

    def get_selected_type(self) -> RotateType:
        """選択された回転タイプを返す

        Returns:
            RotateType: 選択された回転タイプ
        """
        return self.current_rotate_type

    def _on_button_pressed(self) -> None:
        """回転タイプボタンがクリックされたときの処理"""
        button: QtWidgets.QPushButton = self.sender()  # type: ignore
        if button:
            self.current_rotate_type = RotateType(button.text())
            self._change_all_button_style()
            self.pressed_rotate_type_signal.emit(self.current_rotate_type)

    def _on_button_released(self) -> None:
        """回転タイプボタンが離されたときの処理"""
        self.released_rotate_type_signal.emit()

    def _change_all_button_style(self) -> None:
        """すべてのボタンのスタイルを変更する"""
        for button in self.rotate_type_buttons:
            if button.text() == self.current_rotate_type:
                button.setStyleSheet("background-color: #5f9ea0;")
            else:
                button.setStyleSheet("")


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
        self.ui.match_info_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.match_info_table_view.horizontalHeader().setStretchLastSection(True)
        self.ui.match_info_table_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.match_info_table_view.customContextMenuRequested.connect(self._open_table_menu)
        self.ui.match_info_table_view.doubleClicked.connect(self._on_double_click_table)

        # シグナルとスロットの接続
        self.ui.match_button.clicked.connect(self.match_fk_to_ik_controller)
        self.ui.add_button.clicked.connect(self.add_match_info)
        self.ui.manual_action.triggered.connect(self._open_manual_url)

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
        match_info: MatchInfo = self.ui.match_info_table_view.model().data(index, UserRole.MatchInfo)
        if not match_info:
            QtWidgets.QMessageBox.warning(self, "選択エラー", "マッチ情報が見つかりません。")
            return

        if index.column() == HEADERS.index(HEADER_FK_CTRL):  # FKコントローラーの列
            self._select_fk_controller()
        elif index.column() == HEADERS.index(HEADER_JOINT):  # ジョイントの列
            self._select_joint()
        elif index.column() == HEADERS.index(HEADER_ROTATE_TYPE):  # 回転タイプの列
            rotate_type_dialog = RotateTypeDialog(match_info.type, self)
            rotate_type_dialog.pressed_rotate_type_signal.connect(self._on_rotate_type_dialog_button_pressed)
            rotate_type_dialog.released_rotate_type_signal.connect(self._on_rotate_type_dialog_button_released)

            if rotate_type_dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
                selected_match_info = self.ui.match_info_table_view.model().data(index, UserRole.MatchInfo)
                if selected_match_info:
                    selected_match_info.type = rotate_type_dialog.get_selected_type()
                    self.match_fk_to_ik.match_infos.edit(selected_match_info.fk_ctrl, selected_match_info)
                    self.ui.match_info_table_view.model().layoutChanged.emit()
                else:
                    QtWidgets.QMessageBox.warning(self, "選択エラー", "回転タイプを選択できませんでした。")

    def _on_rotate_type_dialog_button_pressed(self, rotate_type: RotateType) -> None:
        """回転タイプダイアログのボタンが押されたときの処理"""
        selected_index = self.ui.match_info_table_view.currentIndex()
        if not selected_index.isValid():
            return
        match_info = self.ui.match_info_table_view.model().data(selected_index, UserRole.MatchInfo)
        if match_info:
            match_info.type = rotate_type
            # TODO ここで回転タイプをmodelには適用しないままmatchを実行する処理を追加する
            self.match_fk_to_ik_controller()

    def _on_rotate_type_dialog_button_released(self) -> None:
        """回転タイプダイアログのボタンが離されたときの処理"""
        undo()

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

    def _open_manual_url(self) -> None:
        """マニュアルのURLを開く"""
        manual_url = "https://github.com/yus3554/MayaFKtoIK"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(manual_url))

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
