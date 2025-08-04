import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import CreateOrderSerializer, VerifyPaymentSerializer
from django.shortcuts import render

#Razorpay client initialization.....
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



def payment_test_view(request):
    return render(request, 'payment_app/payment.html')

class CreateOrderView(APIView):
    @swagger_auto_schema(request_body=CreateOrderSerializer)
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['payment_capture'] = 1
            order = client.order.create(data)
            return Response(order, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    @swagger_auto_schema(request_body=VerifyPaymentSerializer)
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': data['razorpay_order_id'],
                    'razorpay_payment_id': data['razorpay_payment_id'],
                    'razorpay_signature': data['razorpay_signature'],
                })
                return Response({'message': 'Payment verified'}, status=status.HTTP_200_OK)
            except razorpay.errors.SignatureVerificationError:
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)