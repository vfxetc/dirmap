from setuptools import setup, find_packages

setup(
    
    name='dirmap',
    version='0.1.0',
    description='Directory remapper.',
    url='http://github.com/vfxetc/dirmap',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    include_package_data=True,
    
    author='Mike Boers',
    author_email='floss+dirmap@vfxetc.com',
    license='BSD-3',
    
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)
