from setuptools import setup, find_packages

setup(name='fennec',
      version='0.1',
      description='Common fennec functions',
      url='https://github.com/Rhinops-Sela/components',
      author='Fennec',
      author_email='fennec@sela.co.il',
      license='MIT',
      packages=find_packages(),
      package_data={'': ['*.html','info.png']},
      include_package_data=True,
      zip_safe=False)
