from importlib import util
from pathlib import Path
from setuptools import setup

vspec = util.spec_from_file_location(
    "version",
    str(Path(__file__).resolve().parent / "prdb" / "version.py"),
)
vmod = util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, "__version__")

REPO_URL = "https://github.com/yoogottamk/prdb"

current_dir = Path(__file__).resolve().parent

with open(str(current_dir / "requirements.txt")) as reqs_file:
    reqs = reqs_file.read().split()

setup(
    name="prdb",
    description="python remote debugger(*)",
    packages=["prdb"],
    version=version,
    install_requires=reqs,
    python_requires=">=3.6",
    license="MIT",
    author="Yoogottam Khandelwal",
    author_email="yoogottamk@outlook.com",
    url=REPO_URL,
    include_package_data=True,
)
