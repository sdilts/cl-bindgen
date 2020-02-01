from setuptools import setup

setup(name="cl_bindgen",
      version='0.1.0',
      packages=['cl_bindgen'],
      entry_points={
          'console_scripts': [
              'cl-bindgen = cl_bindgen.__main__:main'
          ]
      },
      )
