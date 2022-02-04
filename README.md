# BeeGFS Telemetry UI

This application displays BeeGFS telemetry data in graph form.

## Installation

The following anaconda install has been tested - other things might work if you have
an environment with PyQt5 installed.

conda env create -f environment.yml
conda activate beegfsmonitor
pip install git+https://github.com/chunglabmit/beegfsmonitor

## Running

You'll have to get connectivity to the Influx database as localhost to run
the GUI. You can either run this on the machine that is running the
beegfs-mon daemon or you can port-forward port 8086 from that machine:

```ssh -L 8086:localhost:8086 my-beegfs-server.my-lab.edu```

After that, just run `beegfs-monitor-ui` and use the menus to display
the telemetry data.
