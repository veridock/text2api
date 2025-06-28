from setuptools import setup, find_packages

setup(
    name="text2api",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        'click>=8.1.7',
        'fastapi>=0.112.0',
        'uvicorn>=0.30.0',
        'pydantic>=2.5.0',
        'httpx>=0.27.0',
        'rich>=13.7.0',
        'python-multipart>=0.0.9',
        'aiofiles>=23.2.1',
        'mcp>=1.0.0',
        'langdetect>=1.0.9',
        'pyyaml>=6.0.1',
        'docker>=6.1.3',
    ],
    entry_points={
        'console_scripts': [
            'text2api=text2api.cli:main',
        ],
    },
)
