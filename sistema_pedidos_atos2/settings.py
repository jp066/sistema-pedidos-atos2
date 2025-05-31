import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-p6my=xa1=6&392ivj=d5+6_ba!m)31n(28j2*&@v!64jjj&86e')

CSRF_COOKIE_DOMAIN = ".fly.dev"  # Ajuste isso para seu domínio se necessário
CSRF_TRUSTED_ORIGINS = [
    'https://sistema-pedidos-atos2.fly.dev',
]
CSRF_COOKIE_SECURE = True
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['sistema-pedidos-atos2.fly.dev', 'localhost', '127.0.0.1']

LOGIN_URL = '/login/'          # para onde o @login_required redireciona
LOGIN_REDIRECT_URL = '/caixa/' # para onde ir depois de logar
LOGOUT_REDIRECT_URL = '/'      # onde cair após sair


# Application definition
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'atos2psje@gmail.com'
EMAIL_HOST_PASSWORD = 'koob vngw kiuu nzrc'  # Ou a senha de app
DEFAULT_FROM_EMAIL = 'ATOS Burguer <atos2psje@gmail.com>'


CAIXA_TOKEN = '152448'
MANUNT = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comandas',
    'caixas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_pedidos_atos2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_pedidos_atos2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'volumes/atos2db/sqlite3.db'),  # Usando o volume
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
