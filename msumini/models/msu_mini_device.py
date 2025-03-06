import time
from typing import Optional

from serial import Serial
from serial.serialutil import SerialException

from ..contacts import *


class MSUMiniDevice:
    def __init__(self, port: str, baud_rate: int, version: str):
        self.port: str = port
        self.baud_rate: int = baud_rate
        self.version: str = version
        self.ser: Optional[Serial] = None

    def _open_serial(self):
        """延迟初始化串口"""
        if self.ser is None:
            self.ser = Serial(self.port, self.baud_rate, timeout=SERIAL_TIMEOUT)
            self.ser.write(DEVICE_INITIAL_COMMAND)
            time.sleep(.1)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        elif not self.ser.is_open:
            self.ser.open()

    def send(self, data: bytes) -> int:
        """
        发送数据到串口，并返回设备的响应。

        :param data: 要发送的字节数据
        :return: 设备返回的字节数据
        """
        self._open_serial()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        if self.ser is None or not self.ser.is_open:
            raise SerialException(f"{self.port} is not exist or not open")
        return self.ser.write(data)

    def recv(self) -> bytes:
        self._open_serial()
        retries = 0
        while retries < MAX_RETRIES:
            recv: bytes = self.ser.read(self.ser.in_waiting)
            print(recv)
            if recv:
                return recv
            retries += 1
            time.sleep(0.1)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None

    def __del__(self):
        self.close()

    def __str__(self):
        return f"{self.__class__.__name__}(port={self.port}, baud_rate={self.baud_rate}, version={self.version})"
