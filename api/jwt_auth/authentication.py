from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication


class JWTAuthentication(BaseJWTAuthentication):
    """
    simplejwt.authenticationのJWTAuthenticationを継承しヘッダーではなく
    クッキーによる認証をする
    """
    def authenticate(self, request):
        # header = self.get_header(request)
        # if header is None:
        #     return None
        raw_token = request.COOKIES.get('access')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

