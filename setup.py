try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

from Cython.Build import cythonize


ext_modules = [
    Extension('parse_info',
              ['parse_info.pyx'],
              extra_compile_args=["-w"]),
    Extension('cleanup_page',
              ['cleanup_page.pyx'],
              extra_compile_args=["-w"])
]

setup(ext_modules=cythonize(ext_modules))

# Console command (Windows):
# python setup.py build_ext --inplace --compiler=msvc

# Run a Cython script directly:
# python -c "import parse_info; parse_info.main()"
# python -c "import cleanup_page; cleanup_page.main()"
