import logging
import crcmod
from resources.response import (
    ModeLabels,
    ModeResponse,
    ValuesResponse
)
from enum import Enum
from resources.timer import timer

logger = logging.getLogger(__name__)


class InverterCommand(Enum):
    QPIGS = 110
    QID = 18
    QFLAG = 15
    QPI = 8
    QMOD = 5

    def cmd(self):
        command = self.name
        nbytes = self.value
        try:
            xmodem_crc_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

            def calc_crc(command):
                global crc
                crc = hex(xmodem_crc_func(command))
                return crc

            calc_crc(command.encode('ISO-8859-1'))  # return crc variable

            crc1 = crc[0:4]
            crc2 = crc[0:2] + crc[4:6]

            crc1 = int(crc1, base=16)
            crc2 = int(crc2, base=16)

            scomm = command + chr(crc1) + chr(crc2) + '\r'
            bcomm = scomm.encode('ISO-8859-1')

            return bcomm
        except Exception as e:
            logging.warning("Making command " + str(e))
            raise


class QueryContextManager:
    def __init__(self, device=None):
        self.device = device
        self.handler = None

    def __enter__(self):
        logger.debug(f"Opening device: {self.device}")
        self.handler = open(self.device, 'rb+')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.handler.close()
        if exc_type:
            logger.error("Error: %s (%s)", exc_value, exc_type)

        logger.debug(f"Closed device: {self.device}")

    def mode(self) -> ModeResponse:
        with timer() as taken:
            logger.debug(f"Query: QMOD")
            response_values = self._exec(InverterCommand.QMOD)
            response = ModeLabels[response_values].response()
            logger.debug(f"Finished: QMOD - {taken():.4f}")

        return response

    def values(self) -> ValuesResponse:
        with timer() as taken:
            logger.debug(f"Query: QPIGS")
            values = self._exec(InverterCommand.QPIGS).split(' ')

            response = ValuesResponse()
            response.GridVoltage = values[0]
            response.GridFrequency = values[1]
            response.ACOutputVoltage = values[2]
            response.ACOutputFrequency = values[3]
            response.ACOutputApparentPower = values[4]
            response.ACOutputActivePower = values[5]
            response.OutputLoadPercent = values[6]
            response.BusVoltage = values[7]
            response.BatteryVoltage = values[8]
            response.BatteryChargingCurrent = values[9]
            response.BatteryCapacity = values[10]
            response.DeviceStatus = values[16]

            logger.debug(f"Finished: QPIGS - {taken():.4f}")

        return response

    def _exec(self, cmd: InverterCommand):
        self.handler.write(cmd.cmd())
        r = self.handler.read(cmd.value)

        response = str(r)
        response = response.rstrip()  # strip trailing spaces
        lastI = response.find('\r')
        response = response[3:lastI - 10]  # cut off b'( and a\xc8\r
        return response


