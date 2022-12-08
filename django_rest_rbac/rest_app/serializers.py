from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_app.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''
    Override JWT Token
    '''
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        user.refresh_token = str(token)
        user.save()
        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def create(self, validate_data):
        if validate_data.get('email'):
            validate_data['email']=validate_data.get('email').lower()
        return User.objects.create_user(**validate_data)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    date_of_birth = serializers.DateField(format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'phone_number', 'country_region']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.date_of_birth = validated_data.get('date_of_birth')
        instance.phone_number = validated_data.get('phone_number')
        instance.country_region = validated_data.get('country_region')
        instance.save()
        return instance