from setuptools import setup, find_packages

setup(
    name="document-manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.0",
        "uvicorn>=0.23.0",
        "sqlalchemy>=2.0.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.1.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
    ],
)