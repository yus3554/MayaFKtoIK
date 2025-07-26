import maya.cmds as cmds  # noqa: INP001 # type: ignore


def undo_decorator(func) -> callable:  # type: ignore
    """Undo decorator for Maya commands"""
    def wrapper(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
        cmds.undoInfo(openChunk=True)  # type: ignore
        try:
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)  # type: ignore
    return wrapper
