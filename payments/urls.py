from django.urls import path
from .views import CreateOrderView, VerifyPaymentView, payment_test_view, razorpay_webhook

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('verify/', VerifyPaymentView.as_view(), name='verify'),
    path('pay/', payment_test_view, name='pay'),
    path('webhook/', razorpay_webhook, name='razorpay_webhook'),
]
