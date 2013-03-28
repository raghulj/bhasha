DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bhasha.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# auto super user creation
AUTO_SUPER_USER_CREATION = True
SUPER_USER_USERNAME = 'admin'
SUPER_USER_PASSWORD = 'secret'
SUPER_USER_EMAIL = 'admin@myhost.com'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
