# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status

from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

import ldap3
import socket

class HybridLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = authenticate(request, username=username, password=password)
            if user:
                # User found and authenticated, create a JWT token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            else:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"detail": f"An error occurred during authentication: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # # --- Try LDAP first ---
        # try:
        #     # Set the LDAP server with a connection timeout
        #     server = ldap3.Server('ldap://tnb.my:389', connect_timeout=10)  # Set a 10 second connection timeout
        #     print(f"Attempting to connect to LDAP for user: {username}")

        #     # Try connecting to the server, use socket timeout as fallback
        #     conn = ldap3.Connection(server, user=f"tnb\\{username}", password=password, auto_bind=True, receive_timeout=10)
            
        #     if conn.bind():
        #         print(f"LDAP bind successful for {username}")
        #         # LDAP bind successful, authenticate or create Django user
        #         user = authenticate(request, username=username, password=password)
        #         if user is None:
        #             user = User.objects.create_user(username=username)  # Optional: create if not found

        #         # Return JWT
        #         refresh = RefreshToken.for_user(user)
        #         return Response({
        #             "refresh": str(refresh),
        #             "access": str(refresh.access_token),
        #         })
        # except ldap3.core.exceptions.LDAPBindError as e:
        #     return Response({"detail": f"LDAP bind error: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # except socket.timeout as e:
        #     # If there's a timeout error during the connection or response, return a custom message
        #     return Response({"detail": f"Connection to LDAP server timed out: {str(e)}"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        # except socket.gaierror as e:
        #     # Handle DNS lookup failures or other network-related errors
        #     return Response({"detail": f"Network error occurred while trying to connect to LDAP server: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # except Exception as e:
        #     # General exception handler for any other errors
        #     return Response({"detail": f"An unexpected error occurred while connecting to the LDAP server: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # You can adjust the response as per the fields you want to return
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })
       