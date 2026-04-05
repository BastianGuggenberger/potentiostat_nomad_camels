#BACKEND CLASS for the head, consisting of pump, LED and weight/force sensor

import logging
import time

#importing helper-packages:
from pathlib import Path
import sys
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
import serial_connection

#backend class "head"
class head():

    #initializing function, sets and defines parameters
    def __init__(self):

        self.logger = logging.getLogger(__name__)

        #variable parameters:
        self.COM_PORT = None #'COM6'
        self.FORCE_CALIBRATION = None #17462 # 1/g
        self.STANDARD_FLOW = None #0.1 # ml/s

        #fixed parameters:
        self.PUMP_OFFSET = 0.9 # mm
        self.SYRINGE_CALIBRATION = 5.8 # mm/ml
        self.MAX_VOLUME = 10.0 # ml

        #Serial Connection
        self.connection = None

        # State Dictionary
        self.state = {
            'connected': False,
        }

    #creates serial connection to the hardware
    def connect(self) -> None:
        self.connection = serial_connection.create(com_port=self.COM_PORT)
        try:
            self.connection.open()
        except Exception as e:
            print(e)
        time.sleep(2.0)
        assert serial_connection.receive_data(self.connection) == 'Head Control'
        self.state['connected'] = True

    #disconnects serial connection
    #important for the port to be free again
    def disconnect(self) -> None:
        serial_connection.close(self.connection)
        self.state['connected'] = False

    def parse(self, data: str) -> dict:
        data_dict = {k: v for k, v in [field.split(':') for field in data.split(';')]}
        data_dict['running'] = bool(float(data_dict['running']))
        if data_dict['running']:
            data_dict['position'] = float(data_dict['position'])
            return data_dict
        for k in ('relay1', 'relay2'):
            data_dict[k] = bool(float(data_dict[k]))
        for k in ('position', 'speed', 'acceleration', 'calibration'):
            data_dict[k] = float(data_dict[k])
        for k in ('force', 'led'):
            data_dict[k] = int(data_dict[k])
        return data_dict

    #fundamental function for sending commands to the hardware
    def perform(self, command: str, value: float = 0.0) -> dict:
        try:
            data = serial_connection.send_and_receive_data(self.connection, f'<{command},{value:.5f}>\n')
            return self.parse(data)
        except Exception:
            logging.exception(f'failed to execute command "{command}" with value "{value}"')
            return self.perform(command, value)

    def info(self) -> dict:
        return self.perform('INF')


    #-------------------------------------------------------------------------
    #---------------LOW LEVEL HARDWARE FUNCTIONS------------------------------
    #-------------------------------------------------------------------------

    # ----- Pump functions --------------------------------

    def is_running(self) -> bool:
        return self.info()['running']

    def finish_run(self) -> None:
        while self.is_running():
            time.sleep(0.01)

    def position(self) -> float:
        return self.info()['position']

    #returns current volume
    def volume(self) -> float:
        return self.position() / self.SYRINGE_CALIBRATION

    def stop(self) -> None:
        self.perform('STP')

    def home_raw(self, millimeter: float = 0) -> None:
        self.perform('CAL', self.PUMP_OFFSET)
        self.perform('HOM', millimeter)

    #home: takes the real current volume and registers it
    def home(self, milliliter: float = 0) -> None:
        print("homing Head..")
        self.home_raw(milliliter * self.SYRINGE_CALIBRATION)
        print("Head homed!")

    def set_raw_acceleration(self, millimeter_per_second_squared: float) -> None:
        self.perform('ACC', millimeter_per_second_squared)

    def set_raw_speed(self, millimeter_per_second: float) -> None:
        self.perform('SPD', millimeter_per_second)

    def set_flow(self, milliliter_per_second: float) -> None:
        if milliliter_per_second < 0:
            raise ValueError('flow must be positive')
        self.set_raw_speed(milliliter_per_second * self.SYRINGE_CALIBRATION)

    def set_standard_flow(self) -> None:
        self.set_flow(self.STANDARD_FLOW)

    def set_raw_position(self, millimeter: float) -> None:
        self.perform('POS', millimeter)

    #sets the volume to a new volume
    def set_volume(self, milliliter: float) -> None:
        if milliliter < 0:
            raise ValueError('volume must be positive')
        self.set_raw_position(milliliter * self.SYRINGE_CALIBRATION)
        self.finish_run()

    def set_max_volume(self) -> None:
        self.set_volume(self.MAX_VOLUME)

    def change_volume(self, milliliter: float) -> None:
        new_volume = milliliter + float(self.info()['position']) / self.SYRINGE_CALIBRATION
        if new_volume > self.MAX_VOLUME:
            raise ValueError('volume exceeds pump capacity')
        if(abs(self.volume()-new_volume)<0.001):
            return

        self.set_volume(new_volume)

    # ----- Relay functions --------------------------------

    def switch_relay(self, which: int, on: bool) -> None:
        if which not in [1, 2]:
            raise ValueError('which must be 1 or 2')
        self.perform(f'SW{which}', on)


    # ----- Scale functions --------------------------------

    def tare_scale(self) -> None:
        self.perform('TAR')
        time.sleep(1)

    def raw_force(self) -> int:
        data = self.info()
        if data['running']:
            return 0
        return data['force']

    def gram_force(self) -> float:
        return self.raw_force() / self.FORCE_CALIBRATION


    # ----- LED functions --------------------------------

    def set_led_intensity(self, pwm: int) -> None:
        if not (0 <= pwm <= 255):
            raise ValueError('led intensity pwm must be between 0 and 255')
        self.perform(f'LED', pwm)

    def illuminate(self, duration: float, intensity: float = 1.0) -> None:
        self.set_led_intensity(int(intensity * 255))
        time.sleep(duration)
        self.set_led_intensity(0)



    #-------------------------------------------------------------------------
    #---------------HIGHER LEVEL COMMANDS-------------------------------------
    #-------------------------------------------------------------------------

    # ----- Higher level commands - liquid handling -------------------------------

    #fills head to the given volume (takes care of relays)
    def fill_head(self, volume: float) -> None:
        self.switch_relay(1, False)
        self.switch_relay(2, True)
        self.set_volume(volume + 0.1)
        self.set_volume(volume)

    #purges head to the given volume (takes care of relays)
    def purge_head(self, volume: float) -> None:
        self.switch_relay(1, True)
        self.change_volume(volume)
        self.switch_relay(1, False)
        self.switch_relay(2, True)
        self.set_volume(0.1)
        self.set_volume(0)

    # ----- Higher level commands - touchdown  -------------------------------

    # approaches the sample with the head. sets height so that the head presses on the sample with "target_gram_force".
    def approach(self, object, target_gram_force: float) -> None:
        #time.sleep(1.0)
        self.tare_scale()
        while self.gram_force() < 1.0:
            object.height(-0.1, True)
        step_counter = 0

        #iterative method for approaching target_gram_force
        #difficult to achieve exact results, because stage height is discrete with epsilon=0.01mm
        while(True):
            step_counter += 1
            current_gram_force = self.gram_force()
            difference = target_gram_force - current_gram_force
            if(abs(difference)>4):
                kappa = 0.0015
            elif(abs(difference)>2):
                kappa = 0.0045           
            elif(abs(difference)>1):
                kappa = 0.005
            elif(abs(difference)>0.5):
                kappa=0.002
            else:
                kappa= 0.01
            heightcorrection = - kappa * difference
            if ((difference > 0.5) or (difference < -0.5)):
                object.height(heightcorrection, relative=True)
            else:
                return
            