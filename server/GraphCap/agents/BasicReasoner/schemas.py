from pydantic import BaseModel


class ScratchPad(BaseModel):
    problem_analysis: str
    context_analysis: str
    solution_outline: str
    solution_plan: str


class ChainOfThought(BaseModel):
    scratchpad: ScratchPad
    response: str
