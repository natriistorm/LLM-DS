import logging
import time
import os

from fastapi import FastAPI
from src.refiner_types import RefinerInput, RefinerReturnInput
from src.main import provide_llm_with_action


app = FastAPI()


@app.post("/refine", name="Refine a response")
def refine(response: RefinerInput):
    model_opinion = provide_llm_with_action(response.question, response.response)
    return RefinerReturnInput(refined_resp=model_opinion)