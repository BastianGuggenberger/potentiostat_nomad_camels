import logging
import time
import serial_connection


logger = logging.getLogger(__name__)


# Configuration
# -----------------

COM_PORT = 'COM5'
FORCE_CALIBRATION = 17462 # 1/g
PUMP_OFFSETS = [0.9, 0.9, 0.9] # mm
SYRINGE_CALIBRATION = 5.8 # mm/ml
MAX_VOLUME = 10.0 # ml
MAX_FLOW = 0.173 # ml/s
MIN_FLOW = 0.001 # ml/s
STANDARD_FLOW = 0.100 # ml/s


# State Dictionary
# ----------------

state = {
    'connected': False,
}


# Serial Connection
# -----------------

connection = serial_connection.create(com_port=COM_PORT)

def connect() -> None:
    global connection
    connection.open()
    time.sleep(5.0)
    assert serial_connection.receive_data(connection) == 'Solution Mixing'
    state['connected'] = True

def disconnect() -> None:
    global connection
    serial_connection.close(connection)
    state['connected'] = False

def parse(data: str) -> dict:
    data_dict = {k: v for k, v in [field.split(':') for field in data.split(';')]}
    data_dict['running'] = bool(float(data_dict['running']))
    if data_dict['running']:
        data_dict['position'] = [float(v) for v in data_dict['position'].split(',')]
        return data_dict
    for k in ('position', 'speed', 'acceleration', 'calibration'):
        data_dict[k] = [float(v) for v in data_dict[k].split(',')]
    data_dict['relays'] = [bool(float(v)) for v in data_dict['relays'].split(',')]
    return data_dict

def perform(command: str, value1: float = 0.0, value2: float = 0.0, value3: float = 0.0) -> dict:
    try:
        data = serial_connection.send_and_receive_data(
            connection, f'<{command},{value1:.5f},{value2:.5f},{value3:.5f}>\n')
        return parse(data)
    except Exception:
        logging.exception(f'failed to execute command "{command}" with values "{(value1,value2,value3)}"')
        return perform(command, value1, value2, value3)

def info() -> dict:
    return perform('INF')


# Pumps
# -----------------

def is_running() -> bool:
    return info()['running']

def finish_run() -> None:
    while is_running():
        time.sleep(0.01)

def position() -> list[float]:
    return info()['position']

def volume() -> list[float]:
    return [p / SYRINGE_CALIBRATION for p in position()]

def stop() -> None:
    perform('STP')

def home_pumps_raw(millimeter: list[float]) -> None:
    perform('CAL', *PUMP_OFFSETS)
    perform('HOM', *millimeter)

def home_pumps(milliliter: list[float] = None) -> None:
    if milliliter is None:
        milliliter = [0., 0., 0.]
    home_pumps_raw([m * SYRINGE_CALIBRATION for m in milliliter])

def set_raw_acceleration(millimeter_per_second_squared: list[float]) -> None:
    perform('ACC', *millimeter_per_second_squared)

def set_raw_speed(millimeter_per_second: list[float]) -> None:
    perform('SPD', *millimeter_per_second)

def set_flow(milliliter_per_second: list[float] = None) -> None:
    if milliliter_per_second is None:
        milliliter_per_second = [STANDARD_FLOW] * 3
    if any([mps < 0 for mps in milliliter_per_second]):
        raise ValueError('flow must be positive')
    set_raw_speed([mps * SYRINGE_CALIBRATION for mps in milliliter_per_second])

def set_raw_position(millimeter: list[float]) -> None:
    perform('POS', *millimeter)

def set_volume(milliliter: list[float] = None, block: bool = True) -> None:
    if milliliter is None:
        milliliter = [MAX_VOLUME] * 3
    if any([m < 0 for m in milliliter]):
        raise ValueError('volume must be positive')
    set_raw_position([m * SYRINGE_CALIBRATION for m in milliliter])
    if block:
        finish_run()

def run_pumps(block: bool = False) -> None:
    set_volume([0., 0., 0.], block)

def change_volume(milliliter: list[float], block: bool = True) -> None:
    new_volume = [m + v for m, v in zip(milliliter, volume())]
    if any([nv > MAX_VOLUME for nv in new_volume]):
        raise ValueError('volume exceeds pump capacity')
    set_volume(new_volume, block)


# Relays
# -----------------

def set_raw_relays(on: list[bool]) -> None:
    perform('SWR', *on)

def set_relays_off() -> None:
    set_raw_relays([False, False, False])

def switch_relay(which: str, on: bool) -> None:
    relays = ['output', 'nitrogen', 'vacuum']
    if which not in relays:
        raise ValueError('which must be "output", "nitrogen", or "vacuum"')
    states = info()['relays']
    states[relays.index(which)] = on
    set_raw_relays(states)
