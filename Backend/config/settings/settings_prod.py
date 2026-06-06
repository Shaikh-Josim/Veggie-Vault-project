from VeggieVault.settings import *


DEBUG = False

#Glitchtip settings 
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from logging import INFO, ERROR

sentry_logging = LoggingIntegration( level=INFO, 
event_level= ERROR
) #Capturing Errors in GlitchTip
sentry_sdk.init(
    dsn=os.getenv("GLITCHTIP_DSN"),  # Replace with DSN from your GlitchTip project
    release='VeggieVault@1.0.0',
    integrations=[DjangoIntegration(), sentry_logging],
    traces_sample_rate=1.0,   # Adjust if you want performance monitoring
    send_default_pii=True     # Captures user info if available
)