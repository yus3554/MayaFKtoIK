import maya.cmds as cmds  # noqa: INP001 # type: ignore


def undo_decorator(chunk_name) -> callable:  # type: ignore
    """Undoデコレーター

    Args:
        chunk_name (str): Undoのチャンク名
    """
    def _undo_decorator(func) -> callable:  # type: ignore
        def wrapper(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
            cmds.undoInfo(chunkName=chunk_name, openChunk=True)  # type: ignore
            try:
                return func(*args, **kwargs)
            finally:
                cmds.undoInfo(closeChunk=True)  # type: ignore
        return wrapper
    return _undo_decorator
