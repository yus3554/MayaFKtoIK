import platform  # noqa: INP001
import shutil
import sys
from pathlib import Path

import maya.cmds as cmds  # type: ignore

TOOL_NAME = "MayaFKtoIK"

# TODO ツールの説明を追加する
# TODO リリースしないといけない
# TODO match_info.jsonを固定じゃなくてユーザーが書き出しロードをできるようにする


def install() -> None:
    """MayaFKtoIK ツールを Maya にインストールする関数"""
    # コピー先パス（ユーザーの Modules フォルダ）
    if platform.system() == "Windows":
        user_module_path = Path("~/Documents/maya/modules").expanduser()
    else:
        user_module_path = Path("/usr/autodesk/modeules/Maya")
    user_module_path.mkdir(parents=True, exist_ok=True)

    # 現在の install.py の場所
    current_dir = Path(__file__).resolve().parent
    tool_dir = current_dir
    mod_file = current_dir / f"{TOOL_NAME}.mod"

    # ファイルコピー
    tool_copy_dest_path = user_module_path / TOOL_NAME
    if tool_copy_dest_path.exists():
        shutil.rmtree(tool_copy_dest_path)
    shutil.copytree(tool_dir, tool_copy_dest_path, dirs_exist_ok=True)
    mod_copy_dest_path = user_module_path / f"{TOOL_NAME}.mod"
    if mod_copy_dest_path.exists():
        shutil.rmtree(mod_copy_dest_path)
    shutil.copy2(mod_file, mod_copy_dest_path)

    # Shelf に追加
    shelf_name = "Custom"
    button_label = TOOL_NAME
    command = "import maya_fk_to_ik\nmaya_fk_to_ik.show()"

    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.warning(f"Shelf {shelf_name} does not exist.")
        return

    cmds.shelfButton(
        label=button_label,
        parent=shelf_name,
        command=command,  # type: ignore
        image=(tool_copy_dest_path / "icons" / "maya_fk_to_ik.png").as_posix(),
        annotation=f"Run {TOOL_NAME}",
        sourceType="python",
    )

    # 再起動せずに使えるようにPYTHONPATHを更新
    sys.path.append(str(tool_copy_dest_path / "python"))

    # ツールのインストール完了メッセージ
    cmds.confirmDialog(title="Success", message=f"{TOOL_NAME} installed successfully!", button=["OK"])


def onMayaDroppedPythonFile(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
    """Maya にドロップされたときに呼び出される関数"""
    install()
