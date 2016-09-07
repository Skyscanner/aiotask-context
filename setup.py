from setuptools import setup

install_requires = []
tests_require = install_requires + ['pytest']

setup(
    name="aiotask_context",
    version="0.2",
    author="Manuel Miranda",
    author_email="manu.mirandad@gmail.com",
    description="Store context information inside the asyncio.Task object",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    packages=['aiotask_context'],
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
)
