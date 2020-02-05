from setuptools import setup

requirements = [
    'clang',
    'PyYAML'
]

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    proj_license = f.read()

setup(name="cl_bindgen",
      version='0.1.0',
      description='command line tool and library for creating common lisp language bindings from C header files',
      long_description=readme,
      license=proj_license,
      author="Stuart Dilts",
      author_email='stuart.dilts@gmail.com',
      url='https://github.com/sdilts/cl-bindgen',
      packages=['cl_bindgen'],
      entry_points={
          'console_scripts': [
              'cl-bindgen = cl_bindgen.__main__:main'
          ]
      },
      install_requires=requirements
      )
