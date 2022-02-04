import enum
import influxdb
import numpy as np
import pandas


class Tables(enum.Enum):
    HIGH_RES_META="highResMeta"
    HIGH_RES_STORAGE="highResStorage"
    META_CLIENT_OPS_BY_NODE="metaClientOpsByNode"
    STORAGE_CLIENT_OPS_BY_NODE="storageClientOpsByNode"


class Monitor:
    def __init__(self,
                 host="localhost",
                 port=8086,
                 database="beegfs_mon"):
        self.connection = influxdb.InfluxDBClient(
            host=host, port=port, database=database)

    def query(self, table:Tables) -> pandas.DataFrame:
        table_name = table.value
        result = self.connection.query(f"select * from {table_name}")
        series = result.raw["series"][0]
        columns = series["columns"]
        values = series["values"]
        data = {}
        for i, column in enumerate(columns):
            if column == "time":
                data[column] = np.array([_[i] for _ in values],
                                        np.datetime64)
            else:
                data[column] = np.array([_[i] for _ in values])
        result = pandas.DataFrame(data)
        return result
