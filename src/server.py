import logging
import sys
import time
import os

import uvicorn
from fastapi import FastAPI
from src.refiner_types import RefinerInput, RefinerReturnInput
from src.main import provide_llm_with_action


app = FastAPI()


@app.post("/refine", name="Refine a response")
def refine(response: RefinerInput):
    model_opinion = provide_llm_with_action(response.question, response.response)
    return RefinerReturnInput(refined_resp=model_opinion)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Run `python server.py <HOST> <PORT>`')
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    uvicorn.run('server:app', host=host, port=port, workers=2, reload=True)