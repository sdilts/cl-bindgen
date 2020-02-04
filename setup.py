from setuptools import setup

requirements = [
    'clang',
    'PyYAML'
]

setup(name="cl_bindgen",
      version='0.1.0',
      packages=['cl_bindgen'],
      entry_points={
          'console_scripts': [
              'cl-bindgen = cl_bindgen.__main__:main'
          ]
      },
      install_requires=requirements
      )
