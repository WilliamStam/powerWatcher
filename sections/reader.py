import logging
import json
from datetime import datetime
from resources.response import ReadingResponse

from resources.inverter import QueryContextManager

logger = logging.getLogger(__name__)
class reader():
    def __init__(self,device=None):
        self.device = device

        logger.info(f"Initializing reader: {device}")

    def read(self) -> ReadingResponse:

        with QueryContextManager(self.device) as query:
            logger.debug(f"Getting reading")
            ret = ReadingResponse()
            ret.loadFromDataclass(query.mode())
            ret.loadFromDataclass(query.values())
            logger.debug(json.dumps(ret.toDict(), indent=4))
        return ret