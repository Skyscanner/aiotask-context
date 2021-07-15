from setuptools import setup

install_requires = []
tests_require = install_requires + ['pytest']

setup(
    name="aiotask_context",
    version="0.6.1",
    author="Manuel Miranda",
    author_email="manu.mirandad@gmail.com",
    url="https://github.com/Skyscanner/aiotask-context",
    description="Store context information inside the asyncio.Task object",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    packages=['aiotask_context'],
    install_requires=install_requires,
    tests_require=tests_require,
)
