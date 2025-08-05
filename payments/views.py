import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import CreateOrderSerializer, VerifyPaymentSerializer
from django.shortcuts import render
import json
import hmac
import hashlib
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt



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
    
@csrf_exempt
def razorpay_webhook(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    received_sig = request.headers.get('X-Razorpay-Signature')
    body = request.body.decode('utf-8')

    generated_sig = hmac.new(
        webhook_secret.encode(),
        msg=body.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if received_sig != generated_sig:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    data = json.loads(body)

    # ✅ Process captured payment
    if data['event'] == "payment.captured":
        payment_entity = data['payload']['payment']['entity']
        payment_id = payment_entity['id']
        amount = payment_entity['amount']
        email = payment_entity.get('email')

        # You can update your database here
        print(f"Webhook Payment Captured: {payment_id}, Amount: {amount}, Email: {email}")

        # TODO: Update your Order model/payment record

    return JsonResponse({'status': 'success'})