"""
setup.py that includes modules for the pipeline as well as pip dependencies
"""
import setuptools

setuptools.setup(
    name='traffic-cam',
    version='0.1.0',
    install_requires=[
        'google-api-core==1.16.0',
        'google-apitools==0.5.31',
        'google-cloud-core==1.3.0',
        'google-cloud-storage==1.28.0',
        'google-cloud-vision==0.42.0'
    ],
    packages=setuptools.find_packages(),
)
