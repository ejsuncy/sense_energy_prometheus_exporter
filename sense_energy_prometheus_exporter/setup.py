import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()
version = (here / 'VERSION.txt').read_text(encoding='utf-8')

setuptools.setup(
    name="sense_energy_prometheus_exporter",
    version=version.strip(),
    author="Dan Bunker",
    author_email="dbunked@gmail.com",
    description="A prometheus exporter for Sense energy monitors",
    long_description="A prometheus exporter for Sense energy monitors",
    url="https://github.com/ejsuncy/sense_energy_prometheus_exporter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[]
)
