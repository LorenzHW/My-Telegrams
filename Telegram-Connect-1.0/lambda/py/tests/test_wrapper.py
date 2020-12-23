import unittest
from skill.utils.utils import set_language_model
from tests.tokens import VALID_TOKEN, INVALID_TOKEN
from skill.utils.constants import Constants
from tests.launch_intent.launch_intent_test import LaunchIntentTest
from tests.message_intent.message_intent_test import MessageIntentTest
from tests.reply_intent.reply_intent_test import ReplyIntentTest
from tests.send_intent.send_intent_test import SendIntentTest
from tests.yes_no_intent.yes_no_intent_test import YesNoIntentTest
from tests.settings_intent.settings_test import SettingsIntentTest

if __name__ == "__main__":
    set_language_model('en-US', True)
    Constants.ACCESS_TOKEN = VALID_TOKEN
    suite = unittest.TestSuite()

    suite.addTest(LaunchIntentTest("test_authorized_launch_request"))
    suite.addTest(LaunchIntentTest("test_account_not_linked_launch_request"))
    suite.addTest(LaunchIntentTest("test_account_not_authorized_launch_request"))

    suite.addTest(MessageIntentTest("test_open_message_intent"))
    suite.addTest(MessageIntentTest("test_multiple_telegrams"))

    suite.addTest(ReplyIntentTest("reply_or_next_telegram"))
    suite.addTest(ReplyIntentTest("reply_on_last"))
    suite.addTest(ReplyIntentTest("no_telethon_ids"))

    # TODO: Add test: One-shot start_send_intent
    suite.addTest(SendIntentTest("start_send_intent"))
    suite.addTest(SendIntentTest("ask_for_message"))
    suite.addTest(SendIntentTest("send_telegram"))
    suite.addTest(SendIntentTest("test_multiple_choices"))
    suite.addTest(SendIntentTest("test_send_intent_with_speed_number"))
    suite.addTest(SendIntentTest("german_speed_dial"))

    suite.addTest(SettingsIntentTest("test_first_time_setting_intent"))
    suite.addTest(SettingsIntentTest("test_settings_intent"))

    # TODO: Add yes test on: "Is there anything else I can help you with?
    # TODO: Add no test on: "Is there anything else I can help you with?"
    suite.addTest(YesNoIntentTest("no_intent_on_new_telegrams"))
    suite.addTest(YesNoIntentTest("yes_intent_on_new_telegrams"))
    suite.addTest(YesNoIntentTest("yes_on_send_telegram"))
    suite.addTest(YesNoIntentTest("no_on_send_telegram"))

    # TODO: Add tests for speedIntent

    runner = unittest.TextTestRunner()
    runner.run(suite)
