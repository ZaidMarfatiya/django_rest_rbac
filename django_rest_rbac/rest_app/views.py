from rest_app.serializers import UserSerializer, CustomTokenObtainPairSerializer, ProfileSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate
from rest_app.models import User
from django.utils.encoding import force_bytes, smart_str
from rest_app.helpers import verify_email, forgot_password_email
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated


class UserRegistrationView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, format=None):
        '''
        This method is used to register the user.
        '''
        try:
            email = request.data.get('email').lower()
            if email in User.objects.values_list('email', flat=True):
                return Response({'msg': 'An account with the given email already exists'}, status=status.HTTP_403_FORBIDDEN)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.id))
                verify_email(request, user, uid)
            return Response({'uid': uid, 'email': email,
                             'msg': 'Registration Successful, Email verification link sent. Please verify your email.'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(GenericAPIView):
    def post(self, request, format=None):
        '''
        This method is used to login.
        '''
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user and user.is_verified is False:
            return Response({'errors': {'non_field_errors': ['Please Verify your Email to login']}},
                            status=status.HTTP_404_NOT_FOUND)

        if user and user.is_active is True:
            token = CustomTokenObtainPairSerializer.get_token(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserChangePasswordView(GenericAPIView):

    def post(self, request, format=None):
        '''
        This method is used to change user password.
        '''
        uid = request.data.get('uid')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        current_password = request.data.get('current_password')

        try:
            if User.objects.filter(id=uid).exists():
                user = User.objects.get(id=uid)
                valid_current_password = user.check_password(current_password)
                if not valid_current_password:
                    return Response({"error": "Current password is incorrect."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "User of this id not exists."}, status=status.HTTP_404_NOT_FOUND)
        except:
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

        if user is None or user.is_verified == False:
            return Response({'Error': 'You are not verified user.'}, status=status.HTTP_404_NOT_FOUND)

        if password != password2:
            return Response({"Error": "Password and Confirm Password doesn't match."},
                            status=status.HTTP_401_UNAUTHORIZED)

        user.set_password(password)
        user.save()
        return Response({'Msg': 'Password Changed Successfully.'}, status=status.HTTP_201_CREATED)


class SendPasswordEmailView(GenericAPIView):

    def post(self, request, format=None):
        '''
        This method is used to send password link to email.
        '''
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_verified == True:
                uid = urlsafe_base64_encode(force_bytes(user.id))
                forgot_password_email(request, user, uid)
                return Response({'msg': 'Password link send. Please check your Email'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'Error': 'Please Verify your Email'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': 'You are not registered user.'}, status=status.HTTP_404_NOT_FOUND)


class EditedProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        '''
        This method is used to get user profile.
        '''
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        '''
        This method is used to create user profile.
        '''
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Msg': 'Profile Created Successfully.'},
                        status=status.HTTP_201_CREATED)

    def put(self, request, format=None):
        '''
        This method is used to update user profile.
        '''
        user = request.user

        instance = User.objects.get(id=user.id)
        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'Msg': 'Profile Updated Successfully.'},
                            status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(
                "User Profile doesn't exists, Kindly make a POST request to create a User Profile")