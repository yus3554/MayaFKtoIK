import enum
from typing import Iterator


class RotateVector:
    """FKコントローラーの回転を定義するクラス"""
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self) -> Iterator[float]:
        """イテレータを返す"""
        return iter((self.x, self.y, self.z))


class RotateType(str, enum.Enum):
    """FKコントローラーの回転タイプの定義"""
    TTT = "TTT"
    TTF = "TTF"
    TFT = "TFT"
    TFF = "TFF"
    FTT = "FTT"
    FTF = "FTF"
    FFT = "FFT"
    FFF = "FFF"

    @classmethod
    def from_string(cls, value: str) -> RotateVector:  # noqa: PLR0911
        """文字列からRotateVectorを生成する"""
        if value == "TTT":
            return RotateVector(0, 0, 0)
        if value == "TTF":
            return RotateVector(0, 0, 180)
        if value == "TFT":
            return RotateVector(0, 180, 0)
        if value == "TFF":
            return RotateVector(0, 180, 180)
        if value == "FTT":
            return RotateVector(180, 0, 0)
        if value == "FTF":
            return RotateVector(180, 0, 180)
        if value == "FFT":
            return RotateVector(180, 180, 0)
        if value == "FFF":
            return RotateVector(180, 180, 180)
        msg = f"Unknown rotate type: {value}"
        raise ValueError(msg)
