from importlib.machinery import SourceFileLoader
import os
from pathlib import Path

from setuptools import find_packages, setup

pkg_path = Path("sourced/ml/mining")
sourcedml = SourceFileLoader(
    "sourced-ml-mining", str(pkg_path / "__init__.py")
).load_module()

with (Path(__file__).parent / "README.md").open(encoding="utf-8") as f:
    long_description = f.read()

exclude_packages = (
    ("sourced.ml.mining.tests", "sourced.ml.mining.tests.source")
    if not os.getenv("ML_MINING_SETUP_INCLUDE_TESTS", False)
    else ()
)
include_extensions = ["yaml", "jinja2"]

setup(
    name="sourced-ml-mining",
    description="Tools for mining Git repositories and training machine learning on source "
    "code models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=sourcedml.__version__,
    license="Apache 2.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/ml-mining",
    download_url="https://github.com/src-d/ml-mining",
    packages=find_packages(exclude=exclude_packages),
    namespace_packages=["sourced", "sourced.ml"],
    entry_points={"console_scripts": ["srcdmine=sourced.ml.mining.__main__:main"]},
    keywords=["machine learning on source code", "github", "bblfsh", "babelfish"],
    install_requires=[
        "sourced-ml-core>=0.0.6",
        "PyStemmer>=1.3,<2.0",
        "humanize>=0.5.0,<0.6",
        "clickhouse-driver>=0.1.1,<1.0",
        "scipy>=1.0,<2.0",
        "jinja2>=2.10.1<3.0",
        "pyyaml>=5.1.2<6",
        "scrapy>=1.7.3<2.0",
    ],
    tests_require=["docker>=3.6.0,<4.0"],
    package_data={
        "": ["LICENSE.md", "README.md"],
        "sourced": [
            str(p.relative_to("sourced"))
            for ext in include_extensions
            for p in pkg_path.rglob("*." + ext)
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
)
