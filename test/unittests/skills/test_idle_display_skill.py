import unittest

from ovos_utils.messagebus import FakeBus
from ovos_workshop.skills.base import BaseSkill
from ovos_workshop.skills.idle_display_skill import IdleDisplaySkill


class TestIdleDisplaySkill(unittest.TestCase):
    skill = IdleDisplaySkill(bus=FakeBus(), skill_id="test_idle_skill")

    def test_00_skill_init(self):
        self.assertIsInstance(self.skill, BaseSkill)
        self.assertIsInstance(self.skill, IdleDisplaySkill)
        # TODO: Implement more tests