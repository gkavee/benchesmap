from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy

from fastapi import Response, status

from config import SECRET


class CustomCookieTransport(CookieTransport):
    async def get_login_response(self, token: str) -> Response:
        response = Response(status_code=status.HTTP_200_OK, content=token)
        return self._set_login_cookie(response, token)


cookie_transport = CustomCookieTransport(cookie_name='token', cookie_max_age=24*3600, cookie_secure=True,
                                         cookie_samesite="none")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=24*3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)