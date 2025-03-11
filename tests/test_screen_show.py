import asyncio
import random
import string
import unittest

from PIL import ImageFont, Image, ImageDraw

from msumini import CommandController, image_to_screen, find_msu_mini_devices, DEFAULT_WIDTH, DEFAULT_HEIGHT


def random_str(length: int) -> str:
    chars = string.ascii_letters + string.digits  # 包含大小写字母和数字
    return ''.join(random.choices(chars, k=length))


class TestScreenShow(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.controller: CommandController = CommandController(find_msu_mini_devices())
        self.assertTrue(self.controller.devices, "No device, please check if the device is connected")

    async def test_show_random_string(self):
        image = Image.new("RGB", (DEFAULT_WIDTH, DEFAULT_HEIGHT))
        font = ImageFont.truetype("arial.ttf", 12)
        draw = ImageDraw.Draw(image)
        draw.text(
            (0, 0),
            f"{random_str(32)}\n{random_str(32)}\n{random_str(32)}\n{random_str(32)}\n{random_str(32)}",
            fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            font=font
        )
        image.show()
        data = image_to_screen(image)
        await self.controller.send(data)

    async def asyncTearDown(self):
        for device in self.controller.devices:
            device.close()
        await asyncio.sleep(5)


if __name__ == '__main__':
    unittest.main()
