#BACKEND CLASS for the xyz_stage.
#Directly communicating with the hardware stage with gcode.

import logging
import time
from pathlib import Path
import sys

#importing helper-packages:
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
import serial_connection


#backend class "stage"
class stage():

    logger = logging.getLogger(__name__)

    #initializing function, sets and defines parameters
    def __init__(self):
        
        #variable parameters:
        self.COM_PORT = None #'COM7'
        self.PARKING = None #(141.8, 150.5)
        self.Z_SAFE = None #80.0

        #fixed parameters:
        self.X_MIN = -10.0
        self.X_MAX = 230.0
        self.Y_MIN = -8.0
        self.Y_MAX = 220.0
        self.Z_OFFSET = 0.75
        self.Z_MIN = 0.0
        self.Z_MAX = 250.0 - self.Z_OFFSET

         # Serial Connection
        self.connection = None

        # State Dictionary
        self.state = {
            'connected': False,
            'homed': False
        }

    #connect: creates serial connection to the hardware stage
    def connect(self) -> None:
        print(self.COM_PORT)
        self.connection = serial_connection.create(com_port=self.COM_PORT)
        self.connection.open()
        time.sleep(0.1)
        self.state['connected'] = True

    #disconnect: disconnects serial connection to the hardware stage.
    #important for the port to be free again
    def disconnect(self) -> None:
        serial_connection.close(self.connection)
        self.state['connected'] = False

    #gcode: fundamental function for executing commands in the hardware
    def gcode(self, command: str) -> str:
        return serial_connection.send_and_receive_data(self.connection, f'{command}\n')

    #checkhomestate: checks if stage is homed (with gcode) and homes stage if not.
    def checkhomestate(self):
        posstr = self.gcode("M114") #output:    X:<Position> Y:<Position> Z:<Position> E:<...> Count X:<Steps> Y:<Steps> Z:<Steps>
        #if z_steps = 0 we assume the stage is not homed.
        posstr = posstr.split("Count")[1]
        zcount = int(posstr.split(":")[3])
        if(zcount==0):
            print("stage state: unhomed")
            self.home()
            return
        else:
            print("stage state: homed")
            self.state['homed'] = True
            return

    def finish_move(self) -> None:
        self.gcode('M400')
        serial_connection.send_data(self.connection, 'M118 done\n')
        while serial_connection.receive_data(self.connection) != 'done':
            time.sleep(0.01)

    #current_position: return the current position of the stage (if homed)
    def current_position(self) -> dict:
        data = serial_connection.send_and_receive_data(self.connection, f'M114\n')
        assert serial_connection.receive_data(self.connection) == 'ok'
        return {k: float(v) for k, v in [d.split(':') for d in data.split(' ')[:3]]}

    #home: homes the hardware stage (stage finds out its own position after a reboot)
    def home(self, force: bool = False, moveup: bool = True) -> None:
        if self.state['homed'] and not force:
            return
        
        print("homing Stage..")
        print(self.Z_SAFE)

        if(moveup==True):
            self.height(self.Z_SAFE, True, fast=True)
        
        if force:
            self.gcode('G28')
        else:
            self.gcode('G28 O')
        self.gcode(f'M206 Z{self.Z_OFFSET}')
        self.finish_move()
        print("Stage homed!")
        self.state['homed'] = True

    #position: moves stage to position (x,y)
    def position(self, x: float, y: float, relative: bool = False, fast: bool = False, finishmove = True) -> None:
        self.gcode('G91') if relative else self.gcode('G90')
        self.gcode('G0 F6000') if fast else self.gcode('G0 F1500')
        if (x < self.X_MIN or x > self.X_MAX or y < self.Y_MIN or y > self.Y_MAX) and not relative:
            raise ValueError('Position out of range')
        self.gcode(f'G0 X{round(x, 2)} Y{round(y, 2)}')
        if finishmove == True:
            self.finish_move()

    #height: moves stage to height z
    def height(self, z: float, relative: bool = False, fast: bool = False) -> None:
        if (z < self.Z_MIN or z > self.Z_MAX) and not relative:
            raise ValueError('Height out of range')
        try:
            self.gcode('G91') if relative else self.gcode('G90')
            self.gcode('G0 F6000') if fast else self.gcode('G0 F1500')
            self.gcode(f'G0 Z{round(z, 2)}')
        except Exception as e:
            print(f"[height()] FAILED at z={z}, relative={relative}, fast={fast}: {repr(e)}")
            raise
        self.finish_move()

    #parking: moves stage to parking position
    def parking(self) -> None:
        self.height(self.Z_SAFE, fast=True)
        self.position(self.PARKING, fast=True)
        self.height(10, fast=True)
        self.height(0)

    #testmove: performs a small height move and back
    def testmove(self,) -> None:
        self.height(5, relative=True, fast=True)
        self.height(-5, relative=True, fast=True)

    def shuffle(self,iterations):
        self.height(70)
        self.position(150,150)
        for i in range(iterations):
            self.position(50,50,True,True,False)
            time.sleep(0.2)
            self.position(-50,-50,True,True,False)
            time.sleep(0.2)
            self.position(-50,50,True,True,False)
            time.sleep(0.2)
            self.position(50,-50,True,True,False)
            time.sleep(0.2)

