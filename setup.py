try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A discord bot that gives you weather briefings',
    'author': 'Adnan Valdes',
    'url': 'terminus.earth',
    'download_url': 'terminus.earth',
    'author_email': 'adravaldes@gmail.com',
    'version': '0.1',
    'install_requires': ['discord.py', 'avwx-engine', 'python-dotenv'],
    'scripts': [],
    'name': 'BitB'
}

setup(**config)