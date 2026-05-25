# setup.py (Kısaltmalar Eklenmiş Güncel Sürüm)
from setuptools import setup, find_packages

setup(
    name="autodev-setup",
    version="1.2.0",
    packages=find_packages(),
    py_modules=["main", "config", "templates", "engine"],
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        'console_scripts': [
            # Artık terminal hem uzun adı hem de bu kısaltmaları tanıyacak!
            'setup-my-project=main:cli',
            's-m-p=main:cli',
            'smp=main:cli',
        ],
    },
)