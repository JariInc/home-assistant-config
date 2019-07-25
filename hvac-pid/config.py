import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):

    def getPIDOptions(self, mode):
        prefix = mode.upper()

        return  {
            'Kp': float(os.getenv(f"{prefix}_PID_KP", 2)), 
            'Ki': float(os.getenv(f"{prefix}_PID_KI", 0.01)), 
            'Kd': float(os.getenv(f"{prefix}_PID_KD", 0)),
        }

    def getTempOptions(self, mode):
        return  {
            'temp_min': self.getSetTempMin(),
            'temp_max': self.getSetTempMax(),
            'mode': mode,
        }

    def getSetTempMin(self):
        return float(os.getenv('SET_TEMP_MIN', 7))

    def getSetTempMax(self):
        return float(os.getenv('SET_TEMP_MAX', 30))

    def getWaitTime(self, mode):
        return float(os.getenv(f"{mode.upper()}_PID_INTERVAL", 600))