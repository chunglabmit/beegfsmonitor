from setuptools import setup
try:
    import PyQt5
except ModuleNotFoundError:
    import sys
    print("Please install PyQt5 manually before running setup", file=sys.stderr)
    exit(-1)

install_requires = [
    "influxdb",
    "matplotlib",
    "pandas"
]

setup(
    name="beegfsmonitor",
    version="1.0.0",
    description="UI for viewing BeeGFS telemetry data",
    long_description="This application connects to the influxdb instance "
                     "on the local host to display graphs of the data"
                     "collected by beegfs-mon",
    install_requires=install_requires,
    packages=["beegfsmonitor"],
    entry_points=dict(
        console_scripts=[
            "beegfs-monitor-ui=beegfsmonitor.ui:main"
        ]),
    author="Kwanghun Chung Lab",
    url="https://github.com/chunglabmit/beegfsmonitor",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: Qt",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ]

)