import time
import hardware

def fill_pumps() -> None:
    hardware.set_flow()
    hardware.switch_relay('output', False)
    hardware.set_volume()

def check_pumps(min_pump_volume: float = 3.) -> None:
    if any([v < min_pump_volume for v in hardware.volume()]):
        fill_pumps()

def prime_pumps(reservoir_dead_volume: float = 3., output_dead_volume: float = 1.) -> None:
    hardware.set_flow()
    hardware.switch_relay('vacuum', True)
    hardware.switch_relay('output', False)
    hardware.set_volume([reservoir_dead_volume] * 3)
    hardware.switch_relay('output', True)
    hardware.run_pumps(True)
    hardware.switch_relay('output', False)
    hardware.set_volume([output_dead_volume] * 3)
    hardware.switch_relay('output', True)
    hardware.run_pumps(True)
    hardware.switch_relay('vacuum', False)
    fill_pumps()

def empty_pumps(reservoir_dead_volume: float = 3., output_dead_volume: float = 1.) -> None:
    hardware.set_flow()
    hardware.switch_relay('output', False)
    hardware.run_pumps(True)
    hardware.switch_relay('output', True)
    hardware.set_volume([reservoir_dead_volume + output_dead_volume] * 3)
    hardware.switch_relay('output', False)
    hardware.run_pumps(True)

def mix_solution(ratio1: float = 0., ratio2: float = 0., ratio3: float = 0., volume: float = 2.0,
                 mixing_duration: float = 30.0, min_pump_volume: float = 3.0) -> None:
    check_pumps(min_pump_volume)
    hardware.switch_relay('output', True)
    ratios = [ratio1, ratio2, ratio3]
    hardware.set_flow([r / sum(ratios) * hardware.STANDARD_FLOW for r in ratios])
    hardware.run_pumps()
    time.sleep(volume / hardware.STANDARD_FLOW)
    hardware.stop()
    hardware.switch_relay('output', False)
    time.sleep(mixing_duration)

def discard_solution(vacuum_duration: float = 10.0) -> None:
    hardware.set_relays_off()
    hardware.switch_relay('vacuum', True)
    time.sleep(vacuum_duration)
    hardware.switch_relay('nitrogen', True)
    time.sleep(1)
    hardware.switch_relay('vacuum', False)
