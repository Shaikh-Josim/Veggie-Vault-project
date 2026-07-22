from config.settings.settings_test import *

DATABASES = {
    'default':{
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'Test',
        'USER':'root',
        'PASSWORD':'',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        }
}