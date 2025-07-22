

class RotateType:
    """FKコントローラーの回転タイプを定義するクラス"""
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


class RotateTypes:
    """FKコントローラーの回転タイプの定義"""
    TTT = RotateType(0, 0, 0)
    TTF = RotateType(0, 0, 180)
    TFT = RotateType(0, 180, 0)
    TFF = RotateType(0, 180, 180)
    FTT = RotateType(180, 0, 0)
    FTF = RotateType(180, 0, 180)
    FFT = RotateType(180, 180, 0)
    FFF = RotateType(180, 180, 180)
