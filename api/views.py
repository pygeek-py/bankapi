from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import BlogPost, CustomUser
from .serializers import BlogPostSerializer, UserSerializer, EmailVerificationSerializer, WithdrawSerializer, TransferSerializer
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from rest_framework import permissions, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .services.blockchain import withdraw_token, transfer_within, get_all_user_balances
from django.http import JsonResponse

# Create your views here.
class BlogPostListCreate(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def delete(self, request, *args, **kwargs):
        BlogPost.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def account_inactive(request):
    return Response({'detail': 'Your account is inactive. Please verify your email.'}, status=403)


class BlogPostRetriveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    lookup_field = 'pk'

class BlogPostList(APIView):
    def get(self, request):
        blogposts = BlogPost.objects.all()
        serializer = BlogPostSerializer(blogposts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]



# Email verification endpoint
class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=EmailVerificationSerializer)
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.email_verification_code == code:
            user.is_active = True
            user.email_verification_code = None
            user.save()
            return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='post', request_body=WithdrawSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_view(request):
    user = request.user
    token_address = request.data.get("token_address")
    amount = float(request.data.get("amount"))
    recipient = request.data.get("recipient")

    user_address = user.wallet_address

    print(user_address, amount, token_address)

    result = withdraw_token(
        token_address=token_address,
        recipient=recipient,
        user=user_address,
        amount=amount
    )

    return Response(result)


@swagger_auto_schema(method='post', request_body=TransferSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_view(request):
    user = request.user
    token_address = request.data.get("token_address")
    amount = float(request.data.get("amount"))
    to_address = request.data.get("to_address")

    user_address = user.wallet_address

    print(user_address, amount, token_address)

    result = transfer_within(
        token_address=token_address,
        from_address=user_address,
        to_address=to_address,
        amount=amount
    )

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_balances_view(request):
    try:
        user = request.user
        user_address = user.wallet_address
        balances = get_all_user_balances(user_address)
        return JsonResponse({"status": "success", "data": balances}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)