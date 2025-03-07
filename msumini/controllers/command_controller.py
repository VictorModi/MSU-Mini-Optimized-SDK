import asyncio

from ..contacts import *
from ..models.msu_mini_device import MSUMiniDevice


class CommandController:
    def __init__(self, devices: List[MSUMiniDevice]):
        """
        初始化 CommandController。

        :param devices: 设备列表，用于控制多个设备。
        """
        self.devices: List[MSUMiniDevice] = devices

    async def send(self, data: bytes):
        """
        异步发送数据到所有设备。

        :param data: 发送的字节数据。
        """
        await asyncio.gather(*(asyncio.to_thread(device.send, data) for device in self.devices))

    async def receive(self):
        """
        异步接收所有设备的响应。

        :return: 返回所有设备的响应数据列表。
        """
        return await asyncio.gather(*(asyncio.to_thread(device.recv) for device in self.devices))

    @staticmethod
    def _is_prefix_equals(data: bytes, recv_list) -> bool:
        """
        检查设备响应的数据是否以给定的字节数据为前缀。

        :param data: 期望的前缀字节数据。
        :param recv_list: 设备响应数据列表。
        :return: 如果所有响应的数据以期望的前缀开头，返回 True，否则返回 False。
        """
        print(recv_list)
        for recv in recv_list:
            if len(recv) != 0:
                if recv[0] != data[0] or recv[1] != data[1]:
                    raise AssertionError(f"{data} != {recv}")
        return True

    async def set_lcd_direction(self, reverse: bool = False) -> bool:
        """
        设置 LCD 的显示方向。

        :param reverse: 如果为 True，则设置为反向显示，默认值为 False。
        :return: 如果设置成功，则返回 True，否则返回 False。
        """
        data = bytes([2, 3, 10, 1 if reverse else 0, 0, 0])
        await self.send(data)
        recv_list = await self.receive()
        return self._is_prefix_equals(data, recv_list)

    async def set_lcd_size(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        """
        设置 LCD 的大小（宽度和高度）。

        :param width: 屏幕的宽度（默认值为 DEFAULT_WIDTH）。
        :param height: 屏幕的高度（默认值为 DEFAULT_HEIGHT）。
        """
        data: bytes = bytes([2, 1, width // 256, width % 256, height // 256, height % 256])
        await self.send(data)

    async def set_lcd_starting_position(self, x: int, y: int):
        """
        设置 LCD 的起始位置（X 和 Y 坐标）。

        :param x: 起始位置的 X 坐标。
        :param y: 起始位置的 Y 坐标。。
        """
        data: bytes = bytes([2, 0, x // 256, x % 256, y // 256, y % 256])
        await self.send(data)

    async def set_lcd_size_and_starting_position(self, x: int, y: int, width: int = DEFAULT_WIDTH,
                                                 height: int = DEFAULT_HEIGHT) -> bool:
        """
        设置 LCD 的起始位置和尺寸，并发送控制指令。

        :param x: 起始位置的 X 坐标。
        :param y: 起始位置的 Y 坐标。
        :param width: 屏幕的宽度（默认值为 DEFAULT_WIDTH）。
        :param height: 屏幕的高度（默认值为 DEFAULT_HEIGHT）。
        :return: 设置是否成功，返回 True 或 False。
        """
        await self.set_lcd_starting_position(x, y)
        await self.set_lcd_size(width, height)
        data: bytes = bytes([2, 3, 7, 0, 0, 0, 0])
        await self.send(data)
        recv_list = await self.receive()
        return self._is_prefix_equals(data, recv_list)
