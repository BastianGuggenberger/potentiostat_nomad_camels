from __future__ import annotations
import logging
import serial
import time

logger = logging.getLogger(__name__)

def create(com_port: str, baudrate: int = 115200, timeout: int = 1) -> serial.Serial:
    connection = serial.Serial()
    connection.port = com_port
    connection.baudrate = baudrate
    connection.timeout = timeout
    return connection

def open(connection: serial.Serial) -> None:
    connection.open()

def close(connection: serial.Serial) -> None:
    connection.close()

def send_data(connection: serial.Serial, data: str) -> None:
    connection.reset_input_buffer()
    connection.write(data.encode())

def receive_data(connection: serial.Serial) -> str:
    return connection.readline().decode().strip()

def send_and_receive_data(connection: serial.Serial, data: str, delay: float = 0.1) -> str:
    send_data(connection, data)
    time.sleep(delay)
    return receive_data(connection)
