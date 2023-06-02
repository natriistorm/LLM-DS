from typing import List, Literal, Union, Tuple, Optional
from pydantic import BaseModel, constr, PositiveInt, validator


class RefinerInput(BaseModel):
    question: str
    response: str

class RefinerReturnInput(BaseModel):
    refined_resp: str
