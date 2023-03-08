# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Body, responses, status
from pydantic import BaseModel
import config_handler
import requests

app = FastAPI()

TELEMETRY_URI = os.getenv("TELEMETRY_URI")


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    organization: str


@app.post("/register_user/{user_id}")
def register(user_id: str, user: User):
    # for more information on the data structures take a look at:
    # https://developer.mixpanel.com/docs/data-structure-deep-dive
    response = requests.post(
        f"{TELEMETRY_URI}/register_user/{user_id}",
        json={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "organization": user.organization,
        },
        headers={"Content-Type": "application/json"},
    )
    return responses.PlainTextResponse(status_code=response.status_code)


@app.post("/track/{user_id}/{event}")
def track(user_id: str, event: str, request: dict = Body(...)):
    if config_handler.get_config_value("allow_data_tracking"):
        response = requests.post(
            f"{TELEMETRY_URI}/track/{user_id}/{event}",
            json=request,
            headers={"Content-Type": "application/json"},
        )
        return responses.PlainTextResponse(status_code=response.status_code)
    return responses.PlainTextResponse(status_code=status.HTTP_200_OK)


@app.put("/config_changed")
def config_changed() -> int:
    config_handler.refresh_config()
    return responses.PlainTextResponse(status_code=status.HTTP_200_OK)


@app.get("/healthcheck")
def healthcheck() -> responses.PlainTextResponse:
    headers = {"APP": "OK"}
    return responses.PlainTextResponse("OK", headers=headers)
