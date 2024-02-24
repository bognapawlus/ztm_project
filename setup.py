from setuptools import setup

setup(
    name='ztm_package',
    version='3.0.0',    
    description='ZTM analysis',
    url='https://github.com/bognapawlus/ztm_project',
    author='Bogna Pawlus',
    author_email='bogna.pawlus@gmail.com',
    packages=['analysis', 'download'],
    install_requires=['pandas',
                      'numpy', 
                      'folium',
                      'datetime',
                      'geopy',
                      'unionfind',                          
                      ],

)
