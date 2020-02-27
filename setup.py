from setuptools import setup

requirements = [
    'clang',
    'PyYAML'
]

classifiers = [
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Programming Language :: Python :: 3',
]

with open('README.md') as f:
    readme = f.read()

proj_license = 'MIT'

setup(name="cl_bindgen",
      version='1.1.1',
      description='A command line tool and library for creating Common Lisp language bindings from C header files',
      long_description_content_type='text/markdown',
      long_description=readme,
      license=proj_license,
      author="Stuart Dilts",
      author_email='stuart.dilts@gmail.com',
      url='https://github.com/sdilts/cl-bindgen',
      download_url='https://github.com/sdilts/cl-bindgen/archive/1.1.1.tar.gz',
      packages=['cl_bindgen'],
      entry_points={
          'console_scripts': [
              'cl-bindgen = cl_bindgen.__main__:main'
          ]
      },
      install_requires=requirements,
      classifiers=classifiers
      )
