import re
from os.path import join, exists
import os
from ovos_utils.lang import get_language_dir
from ovos_utils.intents import ConverseTracker
from ovos_utils.log import LOG

# ensure mycroft can be imported
from ovos_utils import ensure_mycroft_import
ensure_mycroft_import()

from mycroft.skills.mycroft_skill import MycroftSkill as _MycroftSkill
from mycroft.skills.fallback_skill import FallbackSkill as _FallbackSkill
from mycroft.skills.skill_data import read_vocab_file, load_vocabulary, \
    load_regex
from mycroft.dialog import load_dialogs


def get_non_properties(obj):
    """Get attibutes that are not properties from object.

    Will return members of object class along with bases down to MycroftSkill.

    Arguments:
        obj:    object to scan

    Returns:
        Set of attributes that are not a property.
    """

    def check_class(cls):
        """Find all non-properties in a class."""
        # Current class
        d = cls.__dict__
        np = [k for k in d if not isinstance(d[k], property)]
        # Recurse through base classes excluding MycroftSkill and object
        for b in [b for b in cls.__bases__ if b not in (object, MycroftSkill)]:
            np += check_class(b)
        return np

    return set(check_class(obj.__class__))


class MycroftSkill(_MycroftSkill):
    monkey_patched = True

    # https://github.com/MycroftAI/mycroft-core/pull/1468
    def _deactivate_skill(self, message):
        skill_id = message.data.get("skill_id")
        if skill_id == self.skill_id:
            self.handle_skill_deactivated(message)

    def handle_skill_deactivated(self, message=None):
        """
        Invoked when the skill is removed from active skill list
        """
        pass

    # https://github.com/MycroftAI/mycroft-core/pull/1468
    def bind(self, bus):
        super().bind(bus)
        if bus:
            ConverseTracker.connect_bus(self.bus)  # pull/1468
            self.add_event("converse.skill.deactivated",
                           self._deactivate_skill)

    # TODO PR not yet made
    def remove_voc(self, utt, voc_filename, lang=None):
        """ removes any entry in .voc file from the utterance """
        lang = lang or self.lang
        cache_key = lang + voc_filename

        if cache_key not in self.voc_match_cache:
            self.voc_match(utt, voc_filename, lang)

        if utt:
            # Check for matches against complete words
            for i in self.voc_match_cache.get(cache_key) or []:
                # Substitute only whole words matching the token
                utt = re.sub(r'\b' + i + r"\b", "", utt)

        return utt


class FallbackSkill(MycroftSkill, _FallbackSkill):
    """ """
