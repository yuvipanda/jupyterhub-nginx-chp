from setuptools import setup

setup(
    name='nchp',
    version='0.1',
    description='NGINX based Configurable HTTP Proxy for use with jupyterhub',
    url='http://github.com/yuvipanda/jupyterhub-nginx-chp',
    author='Yuvi Panda',
    author_email='yuvipanda@riseup.net',
    license='BSD',
    packages=['nchp'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nchp = nchp.__main__:main'
        ]
    }
)
