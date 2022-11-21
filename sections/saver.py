import json
import logging
from datetime import datetime
from resources.response import ReadingResponse
from resources.database import Database
logger = logging.getLogger(__name__)
class saver():
    def __init__(self,database=None):
        self.database = Database(database)
        self.readings = self.database.createTable("readings", {
            "GridVoltage": "NUMERIC",
            "GridFrequency": "NUMERIC",
            "ACOutputVoltage": "NUMERIC",
            "ACOutputFrequency": "NUMERIC",
            "ACOutputApparentPower": "NUMERIC",
            "ACOutputActivePower": "NUMERIC",
            "OutputLoadPercent": "NUMERIC",
            "BusVoltage": "NUMERIC",
            "BatteryVoltage": "NUMERIC",
            "BatteryChargingCurrent": "NUMERIC",
            "BatteryCapacity": "NUMERIC",
            "DeviceStatus": "TEXT",
            "Mode": "TEXT",
            "ModeLabel": "TEXT",
            "ReadingDay": "TEXT",
            "ReadingTime": "TEXT"
        }, indexes={
            "ReadingDay": ["ReadingDay"]
        })

        self.summary = self.database.createTable("summary", {
            "ReadingDay": "TEXT",
            "ReadingHour": "TEXT",
            "PowerOnMode": "NUMERIC",
            "StandbyMode": "NUMERIC",
            "LineMode": "NUMERIC",
            "BatteryMode": "NUMERIC",
            "FaultMode": "NUMERIC",
            "PowerSavingMode": "NUMERIC",
            "Total": "NUMERIC"
        }, indexes={
            "ReadingDay": ["ReadingDay"],
            "ReadingHour": ["ReadingHour"],
        }, unique=['ReadingDay', 'ReadingHour'])

        logger.info(f"Initializing database: {database}")


    def save(self, reading: ReadingResponse = None):
        with self.database.exec() as cursor:
            logger.debug(f"Saving reading")
            cursor.execute(*self.readings.insertSql(reading.toDict()))

            logger.debug(f"Saving summary")
            cursor.execute(*self.summary.insertSql({
                "ReadingDay": datetime.today().strftime('%Y-%m-%d'),
                "ReadingHour": datetime.today().strftime('%H'),
                "PowerOnMode": 1 if reading.Mode == 'P' else 0,
                "StandbyMode": 1 if reading.Mode == 'S' else 0,
                "LineMode": 1 if reading.Mode == 'L' else 0,
                "BatteryMode": 1 if reading.Mode == 'B' else 0,
                "FaultMode": 1 if reading.Mode == 'F' else 0,
                "PowerSavingMode": 1 if reading.Mode == 'H' else 0,
                "Total": 1
            }, upsert={
                "PowerOnMode": "IFNULL(PowerOnMode,0) + excluded.PowerOnMode",
                "StandbyMode": "IFNULL(StandbyMode,0) + excluded.StandbyMode",
                "LineMode": "IFNULL(LineMode,0) + excluded.LineMode",
                "BatteryMode": "IFNULL(BatteryMode,0) + excluded.BatteryMode",
                "FaultMode": "IFNULL(FaultMode,0) + excluded.FaultMode",
                "PowerSavingMode": "IFNULL(PowerSavingMode,0) + excluded.PowerSavingMode",
                "Total": "IFNULL(Total,0) + excluded.Total"
            }))

