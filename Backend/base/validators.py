
from django.core.validators import RegexValidator

logfile_fingerprint_validator = RegexValidator( 
    regex=r'^[a-fA-F0-9]{64}$',
    message="Invalid Logfile Signature ID format. Must follow SHA256 signature."
)