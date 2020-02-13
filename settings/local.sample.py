from gevent import monkey

monkey.patch_all()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'e_ums',
        'USER': 'e_root',
        'PASSWORD': 'XXXX',
        'HOST': 'localhost',
        'PORT': '3306',
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'init_command':
                'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'
        }
    },
}
