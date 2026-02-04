from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from datetime import datetime, timedelta

from app.config import settings

router = APIRouter()


class DiscordCodeExchange(BaseModel):
    code: str


class DiscordUser(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: str | None
    global_name: str | None


class DiscordAuthResponse(BaseModel):
    access_token: str
    user: DiscordUser
    scopes: list[str]
    expires: str


@router.post("/discord/activity", response_model=DiscordAuthResponse)
async def exchange_discord_code(data: DiscordCodeExchange):
    """
    Exchange Discord OAuth2 code for access token.
    Used by Discord Activity to authenticate users.
    """
    if not settings.discord_client_id or not settings.discord_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Discord credentials not configured"
        )

    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": settings.discord_client_id,
                "client_secret": settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": data.code,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to exchange code: {token_response.text}"
            )

        token_data = token_response.json()
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 604800)
        scopes = token_data.get("scope", "").split(" ")

        # Get user info
        user_response = await client.get(
            "https://discord.com/api/users/@me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to get user info"
            )

        user_data = user_response.json()

        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        return DiscordAuthResponse(
            access_token=access_token,
            user=DiscordUser(
                id=user_data["id"],
                username=user_data["username"],
                discriminator=user_data.get("discriminator", "0"),
                avatar=user_data.get("avatar"),
                global_name=user_data.get("global_name"),
            ),
            scopes=scopes,
            expires=expires.isoformat(),
        )
