import json
from VeggieVault.settings import *


#Logs settings
#Logging config using external file
log_setter.set_test_logging_config()

# Database settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Celery settings
CELERY_TASK_ALWAYS_EAGER = "True"
CELERY_TASK_EAGER_PROPAGATES = "True"
