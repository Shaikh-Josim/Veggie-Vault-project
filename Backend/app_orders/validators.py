from django.core.validators import RegexValidator

razorpay_orderid_validator = RegexValidator( 
    regex=r'^order_[A-Za-z0-9]+$',
    message="Invalid Razorpay Order ID format. Must start with 'order_' followed by alphanumeric characters."
)

razorpay_paymentid_validator = RegexValidator( 
    regex=r'^pay_[A-Za-z0-9]+$',
    message="Invalid Razorpay Payment ID format. Must start with 'pay_' followed by alphanumeric characters."
)

razorpay_signature_validator = RegexValidator( 
    regex=r'^[a-fA-F0-9]{64}$',
    message="Invalid Razorpay Signature ID format. Must followed hexadecimal HMAC-SHA256 signature."
)

razorpay_refundid_validator = RegexValidator( 
    regex=r'^rfnd_[A-Za-z0-9]+$',
    message="Invalid Razorpay Refund ID format. Must start with 'rfnd_' followed by alphanumeric characters."
)