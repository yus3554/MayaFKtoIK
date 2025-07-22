import maya.cmds as cmds  # type: ignore

from .core.const import DEFAULT_SETTINGS_FOLDER_PATH
from .core.match_info import MatchInfo, MatchInfosManager
from .core.rotate_type import RotateTypes

DEFAULT_MATCH_INFO_FILE = "match_info.json"


def match_fk_to_ik(info: MatchInfo) -> None:
    """FKコントローラーの回転をIKジョイントに合わせる

    Args:
        info (MatchInfo): マッチ情報を保持するデータクラスのインスタンス
    """
    mat = cmds.xform(info.ik_joint, q=True, ws=True, m=True)  # type: ignore
    cmds.xform(info.fk_ctrl, ws=True, m=mat)  # type: ignore
    cmds.rotate(*info.type, info.fk_ctrl, cs=True, r=True)  # type: ignore


class MatchFKToIK:
    """FKコントローラーの回転をIKジョイントに合わせるためのクラス"""

    def __init__(self) -> None:
        self.match_infos_manager = MatchInfosManager()

        # 初期設定ファイルからマッチ情報を読み込む
        match_info_file = DEFAULT_SETTINGS_FOLDER_PATH / DEFAULT_MATCH_INFO_FILE
        if match_info_file.exists():
            self.match_infos_manager.import_from_file(match_info_file)

    def match(self, character_name: str, fk_ctrl: str) -> None:
        """FKコントローラーに対応するIKジョイントの回転を合わせる

        Args:
            character_name (str): キャラクターの名前
            fk_ctrl (str): FKコントローラーの名前
        """
        match_info = self.match_infos_manager.get(character_name, fk_ctrl)
        if match_info:
            match_fk_to_ik(match_info)
        else:
            cmds.warning(f"No match info found for FK controller: {fk_ctrl}")


# Example usage
ik_joint = "R_leg_5_knee_jnt"
fk_ctrl = "ctrl_FK_R_leg_2_knee"
rotate_type = RotateTypes.FFF
match_info = MatchInfo(ik_joint=ik_joint, fk_ctrl=fk_ctrl, type=rotate_type)
match_fk_to_ik(match_info)


# TODO: GUIで、テーブルを使って、どのFKコントローラーがどのIKジョイントに対応するかを設定できるようにする（今選択しているコントローラーとジョイントを登録するボタンを作る）
# TODO: 回転タイプを選択できるようにする（回転タイプの選択肢をGUIで提供する）これは、クリックしている間は回転タイプが適用された状態がビューに表示され、離したら戻るようにして決めてもらう
# TODO: キャラごとに設定を保存できるようにする（キャラ名をキーにして、設定ファイルを保存する）
# TODO: その設定をもとに、FKコントローラーの回転を自動で設定できるようにする
