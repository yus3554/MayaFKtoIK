from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .rotate_type import RotateType


@dataclass
class MatchInfo:
    """FKコントローラーとIKジョイントのマッチ情報を保持するデータクラス"""
    ik_joint: str
    fk_ctrl: str
    type: RotateType


class MatchInfos:
    """FKコントローラーとIKジョイントのマッチ情報を保持するクラス"""
    def __init__(self) -> None:
        self._data: dict[str, MatchInfo] = {}

    def add(self, ik_joint: str, fk_ctrl: str, rotate_type: RotateType) -> None:
        """マッチ情報を追加する

        Args:
            ik_joint (str): IKジョイントの名前
            fk_ctrl (str): FKコントローラーの名前
            rotate_type (RotateType): FKコントローラーの回転タイプ
        """
        self._data[fk_ctrl] = MatchInfo(ik_joint, fk_ctrl, rotate_type)

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


class MatchInfosManager:
    """マッチ情報を管理するクラス
    キャラごとのマッチ情報を保持し、FKコントローラーとIKジョイントのマッチングを管理する
    """
    def __init__(self) -> None:
        self.match_infos_dict: dict[str, MatchInfos] = {}

    def add(self, character_name: str, match_info: MatchInfo) -> None:
        """キャラごとのマッチ情報を追加する

        Args:
            character_name (str): キャラクターの名前
            match_info (MatchInfo): マッチ情報を保持するデータクラスのインスタンス
        """
        if character_name not in self.match_infos_dict:
            self.match_infos_dict[character_name] = MatchInfos()
        self.match_infos_dict[character_name].add(match_info.ik_joint, match_info.fk_ctrl, match_info.type)

    def get(self, character_name: str, fk_ctrl: str) -> MatchInfo | None:
        """キャラごとのマッチ情報を取得する"""
        if character_name in self.match_infos_dict:
            return self.match_infos_dict[character_name].get(fk_ctrl)
        return None

    def remove(self, character_name: str, fk_ctrl: str) -> None:
        """キャラごとのマッチ情報を削除する

        Args:
            character_name (str): キャラクターの名前
            fk_ctrl (str): FKコントローラーの名前
        """
        if character_name in self.match_infos_dict:
            match_infos = self.match_infos_dict[character_name]
            match_infos.remove(fk_ctrl)

    def clear(self, character_name: str) -> None:
        """キャラごとのマッチ情報をクリアする

        Args:
            character_name (str): キャラクターの名前
        """
        if character_name in self.match_infos_dict:
            del self.match_infos_dict[character_name]

    def edit(self, character_name: str, fk_ctrl: str, new_match_info: MatchInfo) -> None:
        """キャラごとのマッチ情報を編集する

        Args:
            character_name (str): キャラクターの名前
            fk_ctrl (str): FKコントローラーの名前
            new_match_info (MatchInfo): 新しいマッチ情報を保持するデータクラスのインスタンス
        """
        if character_name in self.match_infos_dict:
            match_infos = self.match_infos_dict[character_name]
            match_infos.remove(fk_ctrl)
            match_infos.add(new_match_info.ik_joint, new_match_info.fk_ctrl, new_match_info.type)

    def export(self, file_path: Path) -> None:
        """マッチ情報をJSONファイルにエクスポートする

        Args:
            file_path (str): エクスポート先のファイルパス
        """
        with Path.open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.match_infos_dict, f, ensure_ascii=False, indent=4, default=lambda o: o.__dict__)

    def import_from_file(self, file_path: Path) -> None:
        """JSONファイルからマッチ情報をインポートする

        Args:
            file_path (str): インポート元のファイルパス
        """
        with Path.open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for character_name, match_infos in data.items():
                if character_name not in self.match_infos_dict:
                    self.match_infos_dict[character_name] = MatchInfos()
                for info in match_infos:
                    self.match_infos_dict[character_name].add(info["ik_joint"], info["fk_ctrl"], RotateType(**info["type"]))
