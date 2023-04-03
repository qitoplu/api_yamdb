from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Сочетание "me" нельзя использовать в качестве никнейма.'
            )
        return username

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.email_user(
            subject='confirmation_code',
            message=user.confirmation_code,
            fail_silently=False
        )
        return {
            'email': user.email,
            'username': user.username,
        }


class TokenSerializer(serializers.ModelSerializer, TokenObtainPairSerializer):

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['password'].required = False

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
        }
        confirm_code = None
        if 'request' in self.context:
            authenticate_kwargs['request'] = self.context['request']
            confirm_code = self.context['request'].data['confirmation_code']

        self.user = authenticate(**authenticate_kwargs)

        if self.user is None:
            raise NotFound(
                'User does not exist.'
            )

        if self.user.confirmation_code != confirm_code:
            raise serializers.ValidationError(
                'Invalid confirmation_code.'
            )

        access = AccessToken.for_user(self.user)

        return {
            'token': str(access)
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role'
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'role': user.role,
        }
