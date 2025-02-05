from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from jobs.firebase.auth import Auth, AuthUser
from jobs.config import app_config
import logging


ALLOWED_IPS = ["127.0.0.1", "192.168.0.107"]


def get_auth_user(request: Request) -> AuthUser:
    try:
        client = request.client
        assert client
        logging.info(f"auth -> {client.host}")
        if client.host in ALLOWED_IPS:
            return
        token = request.headers.get("x-user-token", "")
        logging.debug(f"token from header {token}")
        assert token
        auth_user = Auth().verify_token(token)
        assert auth_user
        return auth_user
    except AssertionError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )   


class Authorization:

    async def __call__(self, request: Request):
        return get_auth_user(request=request)

            
class AdminAuthorization:

    async def __call__(self, request: Request):
        try:
            auth_user = get_auth_user(request=request)
            assert auth_user.uid in app_config.access.admin
        except AssertionError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Forbidden"
            )     
    

check_auth = Authorization()
check_admin = AdminAuthorization()
