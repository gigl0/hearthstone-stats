from fastapi import APIRouter
import requests
import os

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/callback")
def callback(code: str):
    client_id = os.getenv("BLIZZARD_CLIENT_ID")
    client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")

    token_url = "https://oauth.battle.net/token"
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": "http://localhost:8000/auth/callback"}

    response = requests.post(token_url, data=data, auth=(client_id, client_secret))
    return response.json()
