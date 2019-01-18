from setuptools import find_packages, setup

setup(
    name="ereuse-tag",
    version='0.0.1a1',
    packages=find_packages(),
    url='https://github.com/ereuse/tag',
    license='BSD',
    author='eReuse.org team',
    author_email='x.bustamante@ereuse.org',
    description='Tag database for eReuse.org',
    install_requires=[
        'click',
        'marshmallow_enum',
        'hashids',
        'teal>=0.2.0a25',
        'psycopg2-binary'
    ],
    tests_requires=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Affero License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
