import logging
import re
import sys
import time
from typing import Optional

from serial import Serial
from serial.serialutil import SerialException

from serial.tools.list_ports import comports
from .contacts import *
from .models.msu_mini_device import MSUMiniDevice


def _scan_port(port_name: str, baud_rate: int) -> Optional[MSUMiniDevice]:
    """ 扫描指定串口，尝试获取设备的响应并解析版本号 """
    try:
        with Serial(port_name, baud_rate, timeout=SERIAL_TIMEOUT) as ser:
            start_time = time.time()
            # 持续检查直到有数据或超时
            while time.time() - start_time < SERIAL_TIMEOUT:
                if ser.in_waiting > 0:
                    recv = ser.read(ser.in_waiting)
                    if DEVICE_RESPONSE_PREFIX in recv:
                        match = re.search(rb"MSN(\d+)", recv)
                        version = match.group(1).decode() if match else "Unknown"
                        return MSUMiniDevice(port_name, baud_rate, version)
                time.sleep(0.05)  # 每 50 毫秒检查一次
    except SerialException as e:
        logging.error(f"Error connecting to {port_name}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while accessing {port_name}: {e}")
    return None


def _get_device_port_name(device_name: str) -> str:
    if sys.platform.startswith("win"):
        return device_name
    else:
        return f"/dev/{device_name}"


def find_msu_mini_device(baud_rate: int = DEFAULT_BAUD_RATE) -> Optional[MSUMiniDevice]:
    """ 扫描串口设备，找到符合条件的 MSUMiniDevice，并解析版本号 """
    devices_list = [
        info for info in comports()
        if not any(description in info.description for description in SERIAL_EXCEPTION_DESCRIPTION)
    ]
    if not devices_list:
        return None

    for info in devices_list:
        port_name = _get_device_port_name(info.name)

        device = _scan_port(port_name, baud_rate)
        if device:
            return device

    return None


def find_msu_mini_devices(baud_rate: int = DEFAULT_BAUD_RATE) -> List:
    """ 扫描串口设备，找到符合条件的所有 MSUMiniDevice 并解析版本号 """
    devices_list = [
        info for info in comports()
        if not any(description in info.description for description in SERIAL_EXCEPTION_DESCRIPTION)
    ]
    if not devices_list:
        return []

    result: List[MSUMiniDevice] = []

    for info in devices_list:
        if sys.platform.startswith("win"):
            port_name = info.device
        else:
            port_name = f"/dev/{info.device}"

        device = _scan_port(port_name, baud_rate)
        if device:
            result.append(device)

    return result


def image_to_screen(image_data: bytearray, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> bytearray:
    """
    处理图像数据，将其转换为适合屏幕显示的字节数组格式。
    参数:
        image_data (bytearray): 输入的图像数据。
        width (int): 屏幕宽度（默认为 128）。
        height (int): 屏幕高度（默认为 128）。
    返回:
        bytearray: 转换后的字节数组，适用于显示或进一步处理。
    """
    result: bytearray = bytearray()  # 存储处理后的结果

    # 计算需要处理的页面数量（每个页面是128字节）
    total_pages = (width * height) // 128

    # 处理每个页面的数据
    for page_idx in range(total_pages):
        page_data = image_data[:128]
        image_data = image_data[128:]

        # 用于存储当前页面的指令
        instructions = []

        # 处理每个指令（每个指令由 2 字节组成）
        for i in range(64):
            instruction = page_data[i * 2] * 65536 + page_data[i * 2 + 1]
            instructions.append(instruction)

        # 找到出现次数最多的指令（众数）
        most_frequent = max(set(instructions), key=instructions.count)

        # 开始当前页面的处理结果
        result.extend([2, 4])  # 当前页面的头部
        result.extend(process_instruction(most_frequent))

        # 处理页面中其余的指令
        for i in range(64):
            if instructions[i] != most_frequent:
                result.append(4)
                result.append(i)
                result.extend(process_instruction(instructions[i]))

        # 页面结束（根据需要调整）
        result.extend([2, 3, 8, 1, 0, 0])

    # 如果还有剩余数据（即数据的字节数不能整除256）
    if (width * height * 2) % 256 != 0:
        remaining_data = image_data
        remaining_data.extend([0xffff] * (256 - len(remaining_data)))

        for i in range(64):
            result.append(4)
            result.append(i)
            result.extend(process_instruction(remaining_data[i * 2] * 65536 + remaining_data[i * 2 + 1]))

        result.extend([2, 3, 8, 0, (width * height * 2) % 256, 0])

    return result


def process_instruction(instruction: int) -> list[int]:
    """
    将一个指令转换为对应的字节值。
    参数:
        instruction (int): 需要转换的指令。
    返回:
        list[int]: 指令的字节数组表示。
    """
    return [
        instruction >> 24,  # 高位字节 1
        (instruction >> 16) & 0xFF,  # 高位字节 2
        (instruction >> 8) & 0xFF,  # 低位字节 1
        instruction & 0xFF  # 低位字节 2
    ]
