from importlib.machinery import SourceFileLoader
import io
import os.path

from setuptools import find_packages, setup

sourcedml = SourceFileLoader("sourced-ml-mining", "./sourced/ml/mining/__init__.py").load_module()

with io.open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

tf_requires = ["tensorflow>=1.0,<2.0"]
tf_gpu_requires = ["tensorflow-gpu>=1.0,<2.0"]
exclude_packages = (
    ("sourced.ml.mining.tests", "sourced.ml.mining.tests.source")
    if not os.getenv("ML_MINING_SETUP_INCLUDE_TESTS", False)
    else ()
)


setup(
    name="sourced-ml-mining",
    description="Framework for mining large repositories to be used in machine learning on source "
                "code. Provides API and tools to mine source code at scale.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=sourcedml.__version__,
    license="Apache 2.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/ml-mining",
    download_url="https://github.com/src-d/ml-mining",
    packages=find_packages(exclude=exclude_packages),
    namespace_packages=["sourced"],
    keywords=[
        "machine learning on source code",
        "github",
        "bblfsh",
        "babelfish",
    ],
    install_requires=[
        "sourced-ml-core",
        "PyStemmer>=1.3,<2.0",
        "sourced-jgit-spark-connector>=2.0.1,<2.1.0",
        "humanize>=0.5.0,<0.6",
        "parquet>=1.2,<2.0",
    ],
    extras_require={"tf": tf_requires, "tf_gpu": tf_gpu_requires},
    tests_require=["docker>=3.6.0,<4.0"],
    package_data={
        "": ["LICENSE.md", "README.md"],
        "sourced.ml.mining.tests": ["./asdf/*.asdf", "./swivel/*", "identifiers.csv.tar.gz"],
    },
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
)
