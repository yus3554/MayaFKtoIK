from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from .rotate_type import RotateType


@dataclass
class MatchInfo:
    """FKコントローラーとジョイントのマッチ情報を保持するデータクラス"""
    joint: str
    fk_ctrl: str
    type: RotateType


class MatchInfos:
    """FKコントローラーとジョイントのマッチ情報を保持するクラス"""
    def __init__(self) -> None:
        self._data: dict[str, MatchInfo] = {}

    def __len__(self) -> int:
        """マッチ情報の数を取得する"""
        return len(self._data)

    def __iter__(self) -> Iterator[MatchInfo]:
        """マッチ情報をイテレートする"""
        return iter(self._data.values())

    def add(self, fk_ctrl: str, joint: str, rotate_type: RotateType) -> None:
        """マッチ情報を追加する

        Args:
            fk_ctrl (str): FKコントローラーの名前
            joint (str): ジョイントの名前
            rotate_type (RotateType): FKコントローラーの回転タイプ
        """
        if fk_ctrl in self._data:
            msg = f"FK controller '{fk_ctrl}' already exists in match info."
            raise ValueError(msg)
        self._data[fk_ctrl] = MatchInfo(joint, fk_ctrl, rotate_type)

    def get(self, fk_ctrl: str) -> MatchInfo | None:
        """FKコントローラーに対応するマッチ情報を取得する

        Args:
            fk_ctrl (str): FKコントローラーの名前

        Returns:
            MatchInfo: FKコントローラーに対応するマッチ情報
        """
        return self._data.get(fk_ctrl)

    def remove(self, fk_ctrl: str) -> None:
        """FKコントローラーに対応するマッチ情報を削除する

        Args:
            fk_ctrl (str): FKコントローラーの名前
        """
        if fk_ctrl in self._data:
            del self._data[fk_ctrl]
        else:
            print(f"No match info found for FK controller: {fk_ctrl}")  # noqa: T201

    def edit(self, fk_ctrl: str, new_match_info: MatchInfo) -> None:
        """キャラごとのマッチ情報を編集する

        Args:
            fk_ctrl (str): FKコントローラーの名前
            new_match_info (MatchInfo): 新しいマッチ情報を保持するデータクラスのインスタンス
        """
        if fk_ctrl in self._data:
            self._data[fk_ctrl] = new_match_info
        else:
            msg = f"No match info found for FK controller: {fk_ctrl}"
            raise KeyError(msg)

    def export_json(self, file_path: Path) -> None:
        """マッチ情報をJSONファイルにエクスポートする

        Args:
            file_path (str): エクスポート先のファイルパス
        """
        with Path.open(file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=4, default=lambda o: o.__dict__)

    def load_json(self, file_path: Path) -> None:
        """JSONファイルからマッチ情報をロードする

        Args:
            file_path (str): ロード元のファイルパス
        """
        with Path.open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for fk_ctrl, match_info in data.items():
                self._data[fk_ctrl] = MatchInfo(**match_info)
