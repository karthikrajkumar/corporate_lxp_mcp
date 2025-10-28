"""Setup configuration for Corporate LXP MCP Platform"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="corporate-lxp-mcp",
    version="1.0.1",
    author="Corporate LXP Team",
    author_email="dev@company.com",
    description="Corporate Learning Experience Platform with MCP integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/company/corporate-lxp-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "corporate-lxp-api=corporate_lxp_mcp.main:main",
            "corporate-lxp-registry=corporate_lxp_mcp.registry.main:main",
            "corporate-lxp-mcp=corporate_lxp_mcp.mcp_server.main:main",
        ],
    },
)
