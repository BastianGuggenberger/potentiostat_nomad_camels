import time
import struct
import serial
import numpy as np
from enum import IntEnum


class Commands(IntEnum):
    READ_ADC = 1
    WRITE_DAC = 2
    READ_DAC = 3
    WRITE_SWITCH = 4
    WRITE_GAIN = 5
    EXECUTE_VOLTAGE_BATCH = 7
    _WRITE_BUFFER = 8
    _READ_BUFFER = 9
    WRITE_CURRENT_HOLD = 10
    _RESET_BUFFER = 11
    WRITE_SAMPLE_COUNT = 12
    WRITE_AUTO_GAIN = 13
    READ_ANALOG_GAIN = 14
    READ_AUTO_GAIN = 15
    READ_GAIN = 16
    READ_SWITCH = 17
    STOP_CURRENT_HOLD = 18


class Resistors(IntEnum):
    R_1K = 0
    R_10K = 1
    R_100K = 2
    R_1M = 3
    R_10M = 4


class ADC(IntEnum):
    WE_OUT = 0
    RE_OUT = 1
    VREF = 2
    TEMP = 3
    HUMID = 4


class DAC(IntEnum):
    CE_IN = 0
    A_REF = 1
    V_AN = 2


class SwitchState(IntEnum):
    Off = 0
    On = 1


class ProtocolError(RuntimeError):
    pass


class Potentiostat:
    """Robust transaction-based USB-CDC serial interface."""

    OK = b"OK\r\n"
    ERR = b"ERR\r\n"

    def __init__(
        self,
        serial_port: str,
        device_id: int = 1,
        baudrate: int = 115200,
        timeout: float = 0.2,
        idle_gap_s: float = 0.01,  # >2ms required by firmware; 10ms safe
    ):
        self.serial_port = serial_port
        self.device_id = device_id & 0xFF
        self.baudrate = baudrate
        self.timeout = timeout
        self.idle_gap_s = idle_gap_s

        self.ser: serial.Serial | None = None

        # state cached locally
        self._auto_gain = False
        self._switch_state = False
        self.resistor = Resistors.R_1K
        self.resistor_val = 1e3

        self.res_vals = {
            Resistors.R_1K: 1e3,
            Resistors.R_10K: 1e4,
            Resistors.R_100K: 1e5,
            Resistors.R_1M: 1e6,
            Resistors.R_10M: 1e7,
        }

        # scaling ranges (match your intent)
        self._vin_lims = (-5.0, 5.0)
        self._vout_lims = (0.0, 3.3)

    def _select_resistor(self, current_a: float, headroom: float = 0.9):
        """
        Pick highest gain (largest R) that won't saturate the WE_OUT ADC.

        Model: |V_weout| ≈ |I| * R  (sign handled elsewhere)
        headroom: safety fraction (0..1), default 0.9
        """
        i = abs(float(current_a))
        if i == 0:
            return Resistors.R_10M

        # WE_OUT is scaled to voltage output limit, conservative max usable swing:
        v_limit = self._vout_lims[1] * float(headroom)

        # Try from highest gain to lowest gain
        order = [Resistors.R_10M, Resistors.R_1M, Resistors.R_100K, Resistors.R_10K, Resistors.R_1K]
        for r in order:
            if i * self.res_vals[r] <= v_limit:
                return r

        return Resistors.R_1K

    # ---------- connection ----------
    def open(self) -> None:
        self.ser = serial.Serial(
            port=self.serial_port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.timeout,
        )
        # settle time for Windows/CDC; harmless on Linux
        time.sleep(0.05)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def close(self) -> None:
        if self.ser:
            self.ser.close()
        self.ser = None

    def connect(self) -> None:
        self.open()
        # Sync state from device
        self._switch_state = self.read_switch()
        self.resistor = self.read_gain()
        self.resistor_val = self.res_vals[self.resistor]
        self._auto_gain = self.read_auto_gain()
        # safe init
        self.write_dac([DAC.A_REF, DAC.V_AN], [-5.0, 0.0])

    # ---------- low-level serial primitives ----------
    def _require_open(self) -> serial.Serial:
        if not self.ser:
            raise RuntimeError("Serial port is not open.")
        return self.ser

    def drain(self, max_bytes: int = 4096) -> bytes:
        """Read and discard any pending bytes (prevents response mixing)."""
        ser = self._require_open()
        out = bytearray()
        t0 = time.time()
        while True:
            waiting = ser.in_waiting
            if waiting:
                out.extend(ser.read(min(waiting, max_bytes)))
                t0 = time.time()  # extend while data keeps coming
            # stop if quiet for a short moment
            if time.time() - t0 > 0.02:
                break
        return bytes(out)

    def read_exact(self, n: int, timeout_s: float | None = None) -> bytes:
        """Read exactly n bytes or raise ProtocolError."""
        ser = self._require_open()
        if n == 0:
            return b""

        deadline = time.time() + (timeout_s if timeout_s is not None else self.timeout)
        buf = bytearray()
        while len(buf) < n:
            remaining = n - len(buf)
            chunk = ser.read(remaining)
            if chunk:
                buf.extend(chunk)
                continue
            if time.time() > deadline:
                raise ProtocolError(f"Timeout reading {n} bytes (got {len(buf)}).")
        return bytes(buf)

    def _pack_frame(self, cmd: int, payload: bytes = b"") -> bytes:
        return bytes([self.device_id, cmd & 0xFF]) + payload

    def send_frame(self, cmd: Commands, payload: bytes = b"", idle_gap_s: float | None = None) -> None:
        """Send a single command frame and wait the required idle gap."""
        ser = self._require_open()
        frame = self._pack_frame(int(cmd), payload)
        ser.write(frame)
        ser.flush()
        time.sleep(self.idle_gap_s if idle_gap_s is None else idle_gap_s)

    def expect_ok(self) -> None:
        """Read and validate OK/ERR line (fixed-length)."""
        resp = self.read_exact(4)  # "OK\r\n" or "ERR\r\n"
        if resp == self.OK:
            return
        if resp == self.ERR:
            raise ProtocolError("Device returned ERR.")
        raise ProtocolError(f"Unexpected ACK bytes: {resp!r}")

    def cmd_ok(self, cmd: Commands, payload: bytes = b"") -> None:
        """Command that returns ASCII OK/ERR."""
        self.drain()
        self.send_frame(cmd, payload)
        self.expect_ok()

    def cmd_read(self, cmd: Commands, payload: bytes, n: int) -> bytes:
        """Command that returns n raw bytes (binary)."""
        self.drain()
        self.send_frame(cmd, payload)
        return self.read_exact(n)

    # ---------- helpers ----------
    def _scale_input_voltages(self, v):
        # map vin_lims -> vout_lims
        vmin, vmax = self._vin_lims
        omin, omax = self._vout_lims
        # linear map
        return ( (v - vmin) * (omax - omin) / (vmax - vmin) ) + omin

    def _scale_output_voltages(self, v):
        # map vout_lims -> vin_lims
        omin, omax = self._vout_lims
        vmin, vmax = self._vin_lims
        return ( (v - omin) * (vmax - vmin) / (omax - omin) ) + vmin

    # ---------- command wrappers ----------
    def write_switch(self, state: SwitchState) -> None:
        self.cmd_ok(Commands.WRITE_SWITCH, bytes([int(state) & 0xFF]))
        self._switch_state = bool(state)

    def read_switch(self) -> bool:
        raw = self.cmd_read(Commands.READ_SWITCH, b"", 1)
        val = raw[0]
        self._switch_state = bool(val)
        return self._switch_state

    def write_gain(self, resistor: Resistors) -> None:
        self.cmd_ok(Commands.WRITE_GAIN, bytes([int(resistor) & 0xFF]))
        self.resistor = resistor
        self.resistor_val = self.res_vals[resistor]

    def read_gain(self) -> Resistors:
        raw = self.cmd_read(Commands.READ_GAIN, b"", 1)
        idx = raw[0]
        try:
            r = Resistors(idx)
        except ValueError:
            raise ProtocolError(f"Invalid gain index from device: {idx}")
        self.resistor = r
        self.resistor_val = self.res_vals[r]
        return r

    def write_auto_gain(self, state: bool) -> None:
        self.cmd_ok(Commands.WRITE_AUTO_GAIN, bytes([1 if state else 0]))
        self._auto_gain = state

    def read_auto_gain(self) -> bool:
        raw = self.cmd_read(Commands.READ_AUTO_GAIN, b"", 1)
        self._auto_gain = bool(raw[0])
        return self._auto_gain

    def write_sample_count(self, sample_count: int = 10):
        """
        Set number of ADC samples averaged per channel in firmware.
        """

        if sample_count <= 0:
            raise ValueError("sample_count must be > 0")

        payload = struct.pack("<I", int(sample_count))
        self.cmd_ok(Commands.WRITE_SAMPLE_COUNT, payload)

    def write_dac(self, channels: list[DAC], voltages: list[float]) -> None:
        if len(channels) != len(voltages):
            raise ValueError("channels and voltages must have same length")
        # payload = [ch0 ch1 ...] + float32 values (little endian)
        ch_bytes = bytes([int(c) & 0xFF for c in channels])
        scaled = [float(self._scale_input_voltages(v)) for v in voltages]
        v_bytes = struct.pack("<" + "f" * len(scaled), *scaled)
        self.cmd_ok(Commands.WRITE_DAC, ch_bytes + v_bytes)

    def read_dac(self, channels: list[DAC]) -> list[float]:
        ch_bytes = bytes([int(c) & 0xFF for c in channels])
        raw = self.cmd_read(Commands.READ_DAC, ch_bytes, 4 * len(channels))
        vals = list(struct.unpack("<" + "f" * len(channels), raw))
        return [float(self._scale_output_voltages(v)) for v in vals]

    def read_adc(self, channels: list[ADC]) -> list[float]:
        ch_bytes = bytes([int(c) & 0xFF for c in channels])
        raw = self.cmd_read(Commands.READ_ADC, ch_bytes, 4 * len(channels))
        vals = list(struct.unpack("<" + "f" * len(channels), raw))
        out = []
        for ch, v in zip(channels, vals):
            v = float(self._scale_output_voltages(v))
            if ch == ADC.WE_OUT:
                # V->I conversion using current resistor
                i = v / (-self.resistor_val)
                out.append(i)
            else:
                out.append(v)
        return out

    def read_adc_gain(self, channels: list[ADC]) -> tuple[list[float], Resistors | None]:
        ch_bytes = bytes([int(c) & 0xFF for c in channels])

        n = 4 * len(channels) + (1 if self._auto_gain else 0)
        raw = self.cmd_read(Commands.READ_ANALOG_GAIN, ch_bytes, n)

        data = raw[: 4 * len(channels)]
        vals = list(struct.unpack("<" + "f" * len(channels), data))

        gain_enum = None
        if self._auto_gain:
            gain = raw[-1]
            try:
                gain_enum = Resistors(gain)
            except ValueError:
                raise ProtocolError(f"Invalid gain index from device: {gain}")
            self.resistor = gain_enum
            self.resistor_val = self.res_vals[gain_enum]

        out = []
        for ch, v in zip(channels, vals):
            v = float(self._scale_output_voltages(v))
            if ch == ADC.WE_OUT:
                out.append(v / (-self.resistor_val))
            else:
                out.append(v)

        return out, gain_enum

    # ---------- PID style current holding ----------
    def write_current_hold(
        self,
        target_current_mA: float = 0.0001,
        initial_step_V: float = 0.00015,
        learning_rate: float = 0.05,
        force_gain: bool = False,
    ):
        """
        Start firmware-side current hold control loop.

        Firmware expects payload:
        float32 target_dac_voltage
        float32 initial_step_V
        float32 learning_rate
        """

        # convert mA → A
        target_A = float(target_current_mA) / 1000.0

        # Select resistor unless user forces current one
        if not force_gain:
            r = self._select_resistor(target_A)
            self.write_gain(r)

        # Convert target current → DAC voltage
        # Firmware convention: V = -I * R, then scaled to DAC range
        dac_v = -(target_A * self.resistor_val)
        dac_v = float(self._scale_input_voltages(dac_v))

        payload = struct.pack(
            "<fff",
            dac_v,
            float(initial_step_V),
            float(learning_rate),
        )

        self.cmd_ok(Commands.WRITE_CURRENT_HOLD, payload)

    def write_current_hold_stop(self):
        """
        Stop firmware-side current hold loop.
        """
        self.cmd_ok(Commands.STOP_CURRENT_HOLD)

    # ---------- public convenience methods ----------
    def read_current(self) -> float:
        """Read current (A) between WE and CE."""
        if self._auto_gain:
            vals, _gain = self.read_adc_gain([ADC.WE_OUT])
            return float(vals[0])
        vals = self.read_adc([ADC.WE_OUT])
        return float(vals[0])

    def read_potential(self) -> float:
        """Read potential (V) between WE and RE."""
        if self._auto_gain:
            vals, _gain = self.read_adc_gain([ADC.RE_OUT])
            return float(vals[0])
        vals = self.read_adc([ADC.RE_OUT])
        return float(vals[0])

    def read_potential_current(self) -> tuple[float, float]:
        """Read (V_we-re, I_we-ce)."""
        if self._auto_gain:
            vals, _gain = self.read_adc_gain([ADC.RE_OUT, ADC.WE_OUT])
            v = float(vals[0])
            i = float(vals[1])
            return v, i
        vals = self.read_adc([ADC.RE_OUT, ADC.WE_OUT])
        v = float(vals[0])
        i = float(vals[1])
        return v, i

    def write_potential(self, potential_V: float) -> None:
        """Set potential (V) between WE and RE."""
        # Your DAC.CE_IN channel sets WE-RE in your naming (keep consistent with your existing usage)
        self.write_dac([DAC.CE_IN], [float(potential_V)])

    def read_ocp(self, restore_switch_state: bool = True) -> float:
        """
        Read Open Circuit Potential (OCP) in Volts.
        Temporarily opens CE-WE switch, reads WE-RE potential, optionally restores switch.
        """
        prev = self._switch_state

        # Open the circuit
        self.write_switch(SwitchState.Off)
        time.sleep(0.02)  # let the analog settle a bit

        # If auto-gain is enabled, give it a few reads to settle on a gain
        # (previous code used range(Resistors.R_1M) which was 0..2; we’ll do a small fixed number)
        if self._auto_gain:
            for _ in range(3):
                _ = self.read_potential()
                time.sleep(0.01)

        ocp = self.read_potential()

        # Restore if needed
        if restore_switch_state and prev:
            self.write_switch(SwitchState.On)

        return float(ocp)
    
    # ---------- robust batch voltage writing ----------
    def write_voltage_batch(self, voltages, delay_ms: int):
        """
        Firmware protocol (CMD_DAC_EXECUTE_BATCH):
        - buffer contains float32 DAC setpoints for eDAC_VCEIN, one per step
        - start command payload: <uint32 delay_ms, uint32 count>
        - response per step: <float WEOUT, float REOUT> [+ uint8 gain if auto_gain]
        """

        if delay_ms < 0:
            raise ValueError("delay_ms must be >= 0")

        # Ensure no current-hold loop is running
        self.write_current_hold_stop()
        time.sleep(0.02)

        v = np.asarray(voltages, dtype=np.float32)
        n_steps = int(v.size)
        if n_steps == 0:
            return np.zeros((0, 2), dtype=np.float32)

        # Scale from actual (-5..5) into device (0..3.3) BEFORE sending (as your firmware expects)
        v_scaled = np.asarray([self._scale_input_voltages(float(x)) for x in v], dtype=np.float32)
        tx_bytes = v_scaled.tobytes(order="C")  # 4 * n_steps bytes
        assert len(tx_bytes) == 4 * n_steps

        # Firmware RX buffer capacity in bytes and steps
        RX_BUF_BYTES = 24000  # CMD_RX_BUFFER_SIZE from QueryList.h

        # Result frame size per step
        step_rx = 8 + (1 if self._auto_gain else 0)

        # --- helper: buffer write (NO ACK) ---
        def buffer_write(payload: bytes):
            # Send CMD_BUFFER_WRITE with payload; firmware does not respond
            # Keep each payload small enough (USB CDC packet constraints / your earlier chunking)
            self.send_frame(Commands._WRITE_BUFFER, payload, idle_gap_s=0.002)

        # --- reset buffer index to 0 (ACK) ---
        self.cmd_ok(Commands._RESET_BUFFER, struct.pack("<I", 0))

        # --- Write strategy ---
        # If it fits entirely, preload all before starting.
        # If not, stream while reading results, respecting the ring buffer capacity.
        out = np.zeros((n_steps, 2), dtype=np.float32)

        max_payload = 254  # keep total frame <= 256 bytes (ID+CMD+payload)
        max_payload -= (max_payload % 4)  # ensure multiple of 4 bytes (float aligned)

        bytes_written = 0
        bytes_consumed = 0

        # Preload as much as we safely can before starting
        preload_bytes = min(len(tx_bytes), RX_BUF_BYTES)
        i = 0
        while i < preload_bytes:
            chunk = tx_bytes[i:i + max_payload]
            buffer_write(chunk)
            i += len(chunk)
        bytes_written = preload_bytes

        # Start batch (delay_ms, count) -> expect OK
        self.cmd_ok(Commands.EXECUTE_VOLTAGE_BATCH, struct.pack("<II", delay_ms, n_steps))

        # For each step: read result, then (if needed) stream more setpoints
        # Use a timeout comfortably above delay to tolerate scheduling/USB jitter.
        per_step_timeout = max(self.timeout, (delay_ms / 1000.0) + 0.5)

        for k in range(n_steps):
            # Read one step response (8 or 9 bytes)
            raw = self.read_exact(step_rx, timeout_s=per_step_timeout)

            we_raw = raw[0:4]
            re_raw = raw[4:8]
            we = struct.unpack("<f", we_raw)[0]
            re = struct.unpack("<f", re_raw)[0]

            # Convert device-scale (0..3.3) back to actual (-5..5)
            we_v = float(self._scale_output_voltages(we))
            re_v = float(self._scale_output_voltages(re))

            if self._auto_gain:
                g = raw[8]
                try:
                    r_ohm = float(self.res_vals[Resistors(g)])
                except ValueError:
                    raise ProtocolError(f"Invalid gain index in batch response: {g}")
            else:
                r_ohm = float(self.resistor_val)

            # Firmware meaning: WEOUT is the shunt/TIA output voltage for current conversion
            # Match your previous convention: current = -(WEOUT / R)
            current_a = -(we_v / r_ohm)

            out[k, 0] = np.float32(current_a)
            out[k, 1] = np.float32(re_v)

            # Streaming: MCU consumes 4 bytes per step from cmd_rx_buffer
            bytes_consumed += 4

            # If more setpoints remain, write them while ensuring we don't lap the consumer
            # Maintain: (bytes_written - bytes_consumed) <= RX_BUF_BYTES - max_payload
            while bytes_written < len(tx_bytes):
                in_flight = bytes_written - bytes_consumed
                if in_flight > (RX_BUF_BYTES - max_payload):
                    break  # too far ahead; wait for next step to consume more

                remaining = len(tx_bytes) - bytes_written
                chunk_len = min(max_payload, remaining)
                # chunk_len is multiple of 4 except possibly at end; but end is also multiple of 4
                chunk = tx_bytes[bytes_written:bytes_written + chunk_len]
                buffer_write(chunk)
                bytes_written += chunk_len

        return out
