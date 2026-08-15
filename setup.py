#!/usr/bin/python

from setuptools import find_packages, setup

install_requires = [
    'requests>=2.31,<3',
    'websockets>=14.1,<16',
]

setup(
    name='signalr-client-aio',
    version='0.0.2',
    author='Stanislav Lazarov',
    author_email='s.a.lazarov@gmail.com',
    license='MIT',
    url='https://github.com/slazarov/python-signalr-client',
    packages=find_packages(exclude=['tests*']),
    install_requires=install_requires,
    python_requires='>=3.9',
    description='Simple Python SignalR client using asyncio.',
    download_url='https://github.com/slazarov/python-signalr-client.git',
    keywords=['signalr', 'signalr-websocket', 'signalr-client', 'signalr-asyncio', 'signalr-aio'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
