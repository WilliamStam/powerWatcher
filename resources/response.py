from dataclasses import (
    asdict,
    dataclass,
    fields
)
from enum import Enum
from datetime import datetime

class BaseResponse:
    def toDict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    def loadFromDict(self, values:dict=dict()):
        for k,v in values.items():
            if hasattr(self,k):
                setattr(self,k,v)

    def loadFromDataclass(self, values = None):
        for field in fields(values):
            if hasattr(self,field.name):
                setattr(self,field.name,getattr(values, field.name))

@dataclass
class ValuesResponse(BaseResponse):
    GridVoltage: float = None
    GridFrequency: float = None
    ACOutputVoltage: float = None
    ACOutputFrequency: float = None
    ACOutputApparentPower: int = None
    ACOutputActivePower: int = None
    OutputLoadPercent: int = None
    BusVoltage: int = None
    BatteryVoltage: float = None
    BatteryChargingCurrent: int = None
    BatteryCapacity: int = None
    DeviceStatus: str = None



@dataclass
class ModeResponse(BaseResponse):
    Mode: str = None
    ModeLabel: str = None

class ModeLabels(Enum):
    P = "Power on mode"
    S = "Standby mode"
    L = "Line Mode"
    B = "Battery mode"
    F = "Fault mode"
    H = "Power saving Mode"

    def response(self) -> ModeResponse:
        return ModeResponse(Mode=self.name,ModeLabel=self.value)


@dataclass
class ReadingResponse(ValuesResponse,ModeResponse, BaseResponse):
    ReadingDay: str = str(datetime.today().strftime('%Y-%m-%d'))
    ReadingTime: str =  str(datetime.today().strftime('%H:%M:%S')),

