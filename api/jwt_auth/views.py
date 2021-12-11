from django.conf import settings
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView 
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .serializers import UserSerializer
from .authentication import JWTAuthentication

import jwt


USER = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenObtainPairView(BaseTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # try:
        serializer.is_valid(raise_exception=True)
        # except TokenError as e:
            # raise InvalidToken(e.args[0])
        resp = Response(data={'message': 'success'})
        resp.set_cookie(key='access',
                            value=serializer.validated_data['access'],
                            httponly=True,)

        resp.set_cookie(key="refresh",
                            value=serializer.validated_data['refresh'],
                            httponly=True,)
        return resp


class TokenRefreshView(BaseTokenRefreshView):
    def post(self, request, *args, **kwargs):
        if access := request.COOKIES.get('access'):
            try:  # アクセストークンの期限が残っているにもかかわらずリフレッシュトークンを取得しようとした場合
                payload = jwt.decode(access, settings.SECRET_KEY, algorithms=['HS256'])
                resp = Response({'message': 'This is a suspicious access. Deleted the tokens.'}, 
                                status=status.HTTP_400_BAD_REQUEST)
                resp.delete_cookie('access')
                resp.delete_cookie('refresh')
                return resp
            except jwt.ExpiredSignatureError:
                pass  # 期限が過ぎているのであればokなのでpass
        
        else:  # アクセストークンがないのにリフレッシュトークンを取得できないはず
            raise InvalidToken()

        refresh = {'refresh': request.COOKIES.get('refresh')}
        serializer = self.get_serializer(data=refresh)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        resp = Response({'message': 'success'})
        resp.set_cookie(key='access',
                        value=serializer.validated_data['access'],
                        httponly=True,)
        return resp


class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)  # permissionとauthenticationクラスを定義しているためrequest.userが使える
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        resp = Response({'message': 'success'})
        resp.delete_cookie('access')
        resp.delete_cookie('refresh')
        return resp