import os
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

TEMPLATE_DEBUG = False

DATABASES = {
	'default':{
		'ENGINE': 'django.db.backends.mysql',
		'NAME': os.environ.get('DB_NAME'),
		'HOST': os.environ.get('DB_HOST'),
		'PORT': os.environ.get('DB_PORT'),
		'USER': os.environ.get('DB_USER'),
		'PASSWORD': os.environ.get('DB_PASSWORD'),
	}
}

ADMINS = (('Yi Zhao', 'zhaoyi.yuan31@gmail.com'),)

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'console':{
			'level': 'INFO',
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console'],
			'propagate': True,
		},
	},
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(BASE_DIR, 'static').replace('\\', '/')
