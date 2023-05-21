from dff.script import Context

from .main import provide_llm_with_action
from dff.script import Context
import requests


def response_refiner(ctx: Context):
    last_request = ctx.last_request
    last_response = ctx.last_response
    if last_response is None:
        # nothing to refine
        return
    response = requests.post(url='http://0.0.0.0:8030/refine',
                             json={
                                 'question':
                                     last_request,
                                 'response':
                                     last_response,
                             })
    model_response = response.json()
    if model_response.get('refined_resp') is None:
        # leave untouched
        ctx.set_last_request(last_request)
    else:
        ctx.set_last_request(model_response['refined_resp'])


services = [response_refiner]  # post-services run after bot sends a response
