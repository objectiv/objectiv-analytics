import os
workers = os.environ.get('WORKERS', 2)
host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', 5000)
bind = f'{host}:{port}'

