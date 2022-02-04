# Boilerplate for this app from
# https://pythonspot.com/pyqt5-matplotlib/
#
import argparse
import numpy as np
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from .monitor import Tables, Monitor
import datetime


class App(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beegfs Telemetry")
        menu_bar = QtWidgets.QMenuBar()
        self.time = "hour"
        time_menu = menu_bar.addMenu("Time")
        self.time_action_group = QtWidgets.QActionGroup(self, exclusive=True)
        self.aday = self.time_action_group.addAction("Day")
        self.aday.setCheckable(True)
        self.aday.setChecked(True)
        time_menu.addAction(self.aday)
        self.ahour = self.time_action_group.addAction("Hour")
        self.ahour.setCheckable(True)
        time_menu.addAction(self.ahour)
        self.aminute = self.time_action_group.addAction("Minute")
        self.aminute.setCheckable(True)
        time_menu.addAction(self.aminute)
        self.query_action_group = QtWidgets.QActionGroup(self, exclusive=True)
        query_menu = menu_bar.addMenu("Query")
        self.a_recv_bytes = self.query_action_group.addAction("Receive Bytes")
        self.a_recv_bytes.setCheckable(True)
        self.a_recv_bytes.setChecked(True)
        query_menu.addAction(self.a_recv_bytes)
        self.a_send_bytes = self.query_action_group.addAction("Send Bytes")
        self.a_send_bytes.setCheckable(True)
        query_menu.addAction(self.a_send_bytes)
        self.a_read_bytes = self.query_action_group.addAction("Read Bytes")
        self.a_read_bytes.setCheckable(True)
        query_menu.addAction(self.a_read_bytes)
        self.a_write_bytes = self.query_action_group.addAction("Write Bytes")
        self.a_write_bytes.setCheckable(True)
        query_menu.addAction(self.a_write_bytes)
        self.a_metadata_receive_bytes = self.query_action_group.addAction("Metadata Receive Bytes")
        self.a_metadata_receive_bytes.setCheckable(True)
        query_menu.addAction(self.a_metadata_receive_bytes)
        self.a_metadata_send_bytes = self.query_action_group.addAction("Metadata Send Bytes")
        self.a_metadata_send_bytes.setCheckable(True)
        query_menu.addAction(self.a_metadata_send_bytes)
        self.a_metadata_per_node = self.query_action_group.addAction("Metadata Per Node")
        self.a_metadata_per_node.setCheckable(True)
        query_menu.addAction(self.a_metadata_per_node)
        self.a_storage_per_node = self.query_action_group.addAction("Storage Per Node")
        self.a_storage_per_node.setCheckable(True)
        query_menu.addAction(self.a_storage_per_node)
        run_menu = menu_bar.addMenu("Run")
        self.arefresh = run_menu.addAction("Refresh")
        for a in self.aday, self.ahour, self.aminute, \
                 self.a_metadata_per_node, self.a_metadata_receive_bytes, \
                 self.a_metadata_send_bytes, self.a_recv_bytes, \
                 self.a_read_bytes, self.a_write_bytes, \
                 self.a_storage_per_node, self.a_send_bytes, self.arefresh:
            a.triggered.connect(self.replot)
        self.setMenuBar(menu_bar)
        self.monitor = Monitor()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        self.figure = Figure(figsize=(8, 8))
        self.static_canvas = FigureCanvas(self.figure)
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between zPyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(self.static_canvas, self))
        layout.addWidget(self.static_canvas)
        self.plot_high_res(Tables.HIGH_RES_STORAGE, "netRecvBytes")
        self.show()

    def replot(self, state):
        self.figure.clf()
        if self.a_metadata_receive_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_META, "netRecvBytes")
        elif self.a_metadata_send_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_META, "netSendBytes")
        elif self.a_recv_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_STORAGE, "netRecvBytes")
        elif self.a_send_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_STORAGE, "netSendBytes")
        elif self.a_read_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_STORAGE, "diskReadBytes")
        elif self.a_write_bytes.isChecked():
            self.plot_high_res(Tables.HIGH_RES_STORAGE, "diskWriteBytes")
        elif self.a_metadata_per_node.isChecked():
            self.plot_meta_ops_by_node()
        elif self.a_storage_per_node.isChecked():
            self.plot_storage_ops_by_node()
        self.static_canvas.draw()

    def plot_high_res(self, table, field):
        df = self.monitor.query(table)
        gb, df, n_sec = self.time_group(df)
        rollup = df.groupby(gb)\
                     [field].sum() / n_sec
        ax = self.figure.add_subplot(111)
        if len(df) == 0:
            ax.set_title(f"{field}: no data")
        else:
            rollup.plot(ax=ax)
            self.set_tickmarks(ax, df)
            ax.set_title(field)

    def set_tickmarks(self, ax, df):
        ax.set_xlabel("")
        tz_name = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        tmin = df["time"].min().to_pydatetime().astimezone(tz_name)
        tmax = df["time"].max().to_pydatetime().astimezone(tz_name)
        tdiff = tmax - tmin
        n_labels = len(ax.get_xticks())
        label_granularity = tdiff / (n_labels - 1)
        times = [tmin + label_granularity * i for i in range(n_labels)]
        ax.set_xticklabels(["%d:%02d:%02d" % (t.hour, t.minute, t.second) for t in times])

    def time_group(self, df):
        if self.aday.isChecked():
            earliest = datetime.datetime.utcnow() - datetime.timedelta(0, 60 * 60 * 24)
            sec = 60 * 60
        elif self.ahour.isChecked():
            earliest = datetime.datetime.utcnow() - datetime.timedelta(0, 60 * 60)
            sec = 60
        else:
            earliest = datetime.datetime.utcnow() - datetime.timedelta(0, 60)
            sec = 1
        df = df[df["time"] >= earliest]
        if self.aday.isChecked():
            gb = [df["time"].dt.date, df["time"].dt.hour]
        elif self.ahour.isChecked():
            gb = [df["time"].dt.date, df["time"].dt.hour, df["time"].dt.minute]
        else:
            gb = [df["time"].dt.date, df["time"].dt.hour, df["time"].dt.minute, df["time"].dt.second]
        return gb, df, sec


    def plot_meta_ops_by_node(self):
        df = self.monitor.query(Tables.META_CLIENT_OPS_BY_NODE)
        df = df[df["time"] > np.datetime64("2022-02-03T13:54")]
        nodes_rollup = dict(list(df.groupby(df["node"])))
        h = int(np.ceil(np.sqrt(len(nodes_rollup))))
        axes = [self.figure.add_subplot(h, h, i+1)  for i in range(len(nodes_rollup))]
        for ax, k in zip(axes, nodes_rollup.keys()):
            subdf = nodes_rollup[k]
            gb, subdf, nsec = self.time_group(subdf)
            if len(subdf) == 0:
                continue
            rollup = subdf.groupby(gb)
            (rollup["stat"].sum() / nsec ).plot(ax=ax)
            ax.set_title(k)
            self.set_tickmarks(ax, subdf)

    def plot_storage_ops_by_node(self):
        df = self.monitor.query(Tables.STORAGE_CLIENT_OPS_BY_NODE)
        df = df[df["time"] > np.datetime64("2022-02-03T13:54")]
        nodes_rollup = dict(list(df.groupby(df["node"])))
        h = int(np.ceil(np.sqrt(len(nodes_rollup))))
        axes = [self.figure.add_subplot(h, h, i+1)  for i in range(len(nodes_rollup))]
        for ax, k in zip(axes, nodes_rollup.keys()):
            subdf = nodes_rollup[k]
            gb, subdf, sec = self.time_group(subdf)
            if len(subdf) == 0:
                continue
            rollup = subdf.groupby(gb)
            (rollup["B-rd"].sum() / sec ).plot(ax=ax, label="B-rd")
            (rollup["B-wr"].sum() / sec ).plot(ax=ax, label="B-wr")
            ax.legend()
            ax.set_title(k)
            self.set_tickmarks(ax, subdf)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

