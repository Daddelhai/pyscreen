import os
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="ATCSim",
    author='Julian Kruchy, Daniel Karamyshev, Lucas Aehlig',
    version="0.1.7",
    packages=["pyscreen"],
    install_requires=[
        "pygame",
        "numpy",
        "aiohttp",
        "click",
        "fastapi",
        "uvicorn[standard]",
        "requests",
        "cryptography",
        "psutil",
        "cython"
    ],
    ext_modules = cythonize(
        [
            "pyscreen/core/angle.pyx",
            "pyscreen/core/vector.pyx",
            "pyscreen/core/distance.pyx",
            "pyscreen/core/altitude.pyx",
            "pyscreen/core/coordinate.pyx",
        ],
        compiler_directives={'language_level' : "3"}
    )
)
