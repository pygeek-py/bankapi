
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import BlogPost
from django.contrib.auth import get_user_model
from .models import CustomUser
from web3 import Web3
from cryptography.fernet import Fernet
from django.conf import settings
from base64 import urlsafe_b64encode

class WithdrawSerializer(serializers.Serializer):
    token_address = serializers.CharField()
    amount = serializers.FloatField()
    recipient = serializers.CharField()

class TransferSerializer(serializers.Serializer):
    token_address = serializers.CharField()
    amount = serializers.FloatField()
    to_address = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('pk', 'email', 'first_name', 'last_name', 'wallet_address', 'public_key')

class CustomLoginSerializer(LoginSerializer):
    def get_auth_user_serializer(self, user):
        class AuthUserSerializer(serializers.ModelSerializer):
            wallet_address = serializers.CharField(source='wallet_address', read_only=True)
            public_key = serializers.CharField(source='public_key', read_only=True)

            class Meta:
                model = user.__class__
                fields = ('pk', 'email', 'first_name', 'last_name', 'wallet_address', 'public_key')

        return AuthUserSerializer(user, context=self.context).data

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name')
        data['last_name'] = self.validated_data.get('last_name')
        return data

    def save(self, request):
        import random
        from django.core.mail import send_mail

        user = super().save(request)
        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        # Generate wallet
        acct = Web3().eth.account.create()
        wallet_address = acct.address
        public_key = acct._key_obj.public_key.to_hex()
        private_key = acct.key.hex()

        # Encrypt private key
        raw_key = getattr(settings, "ENCRYPTION_KEY", None)
        if raw_key is None:
            raise Exception("ENCRYPTION_KEY not set in settings")
        if len(raw_key) != 32:
            raise Exception("ENCRYPTION_KEY must be exactly 32 bytes")
        fernet_key = urlsafe_b64encode(raw_key.encode())
        fernet = Fernet(fernet_key)
        encrypted_private_key = fernet.encrypt(private_key.encode()).decode()

        user.wallet_address = wallet_address
        user.public_key = public_key
        user.encrypted_private_key = encrypted_private_key

        # Generate and send 6-digit code
        code = str(random.randint(100000, 999999))
        user.email_verification_code = code
        user.is_active = False  # User is inactive until verified
        user.save()
        send_mail(
            'Your Email Verification Code',
            f'Your verification code is: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        self.wallet_address = wallet_address
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Only add wallet_address if instance is a CustomUser
        if hasattr(instance, 'wallet_address'):
            data['wallet_address'] = instance.wallet_address
        return data

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'published']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name']

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)