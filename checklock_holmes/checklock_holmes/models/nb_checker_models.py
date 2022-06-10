from typing import Optional

from pydantic import BaseModel


class CellError(BaseModel):
    number: int
    exc: Exception


class NoteBookCheck(BaseModel):
    name: str
    script: str
    completed: bool
    engine: str
    error: Optional[CellError]
    failing_block: Optional[str]
