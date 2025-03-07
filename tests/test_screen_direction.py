import time
import unittest
import msumini
from msumini import CommandController


class TestScreenDirection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        device: msumini.MSUMiniDevice = msumini.find_msu_mini_device()
        self.command_controller: CommandController = CommandController([device])

    async def test_reverse(self):
        self.assertEqual(
            await self.command_controller.set_lcd_direction(reverse=True),
            True
        )

    async def test_forward(self):
        self.assertEqual(
            await self.command_controller.set_lcd_direction(reverse=False),
            True
        )

    async def asyncTearDown(self):
        for device in self.command_controller.devices:
            device.close()
        time.sleep(10)


if __name__ == '__main__':
    unittest.main()
