from __future__ import annotations

import maya.cmds as cmds  # type: ignore

from .core.const import DEFAULT_MATCH_INFO_FILE_NAME, DEFAULT_SETTINGS_FOLDER_PATH
from .core.match_info import MatchInfo, MatchInfos
from .core.rotate_type import RotateType
from .utils.decorator import undo_decorator


@undo_decorator("Match FK to IK")
def match_fk_to_ik(info: MatchInfo) -> None:
    """FKコントローラーの回転をジョイントに合わせる

    Args:
        info (MatchInfo): マッチ情報を保持するデータクラスのインスタンス
    """
    mat = cmds.xform(info.joint, q=True, ws=True, m=True)  # type: ignore
    cmds.xform(info.fk_ctrl, ws=True, m=mat)  # type: ignore
    cmds.rotate(*RotateType.from_string(info.type), info.fk_ctrl, cs=True, r=True)  # type: ignore


class MatchFKToIK:
    """FKコントローラーの回転をジョイントに合わせるためのクラス"""

    def __init__(self) -> None:
        self.match_infos = MatchInfos()

        # 初期設定ファイルからマッチ情報を読み込む
        match_info_file = DEFAULT_SETTINGS_FOLDER_PATH / DEFAULT_MATCH_INFO_FILE_NAME
        if match_info_file.exists():
            self.match_infos.load_json(match_info_file)

    def match(self, fk_ctrl: str, override_match_info: MatchInfo | None = None) -> None:
        """FKコントローラーに対応するジョイントの回転を合わせる

        Args:
            fk_ctrl (str): FKコントローラーの名前
            override_match_info (MatchInfo, optional): 上書きするマッチ情報
        """
        match_info = override_match_info if override_match_info else self.match_infos.get(fk_ctrl)
        if match_info:
            match_fk_to_ik(match_info)
        else:
            cmds.warning(f"No match info found for FK controller: {fk_ctrl}")


def main() -> None:
    """スクリプトのエントリーポイント (例)"""
    joint = "R_leg_5_knee_jnt"
    fk_ctrl = "ctrl_FK_R_leg_2_knee"
    rotate_type = RotateType.FFF
    match_info = MatchInfo(joint=joint, fk_ctrl=fk_ctrl, type=rotate_type)
    match_fk_to_ik(match_info)


if __name__ == "__main__":
    main()
