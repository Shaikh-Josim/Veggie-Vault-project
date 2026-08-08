from VeggieVault.settings import *


#Logs settings
#Logging config using external file
log_setter.set_test_logging_config()

#url_settings
ROOT_URLCONF = "config.settings.test_urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}



# Cache Settings
# settings.py (At the very bottom)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake-cache",
    }
}


# Celery settings
CELERY_TASK_ALWAYS_EAGER = "False"
CELERY_TASK_EAGER_PROPAGATES = "True"




