import unittest

from skill.lambda_function import sb
from tests.launch_intent.launch_request import launch_request
from skill.i18n.language_model import LanguageModel
from tests.tokens import VALID_TOKEN, INVALID_TOKEN
from skill.utils.constants import Constants
from skill.utils.utils import set_language_model


class LaunchIntentTest(unittest.TestCase):
    def test_authorized_launch_request(self):
        i18n = Constants.i18n
        handler = sb.lambda_handler()

        launch_request["context"]["System"]["user"]["accessToken"] = VALID_TOKEN
        launch_request["session"]["user"]["accessToken"] = VALID_TOKEN

        event = handler(launch_request, None)
        ssml = event.get('response').get('outputSpeech').get('ssml')
        ssml = ssml[-7:8]
        self.assertTrue(ssml in i18n.WELCOME or ssml in i18n.USER_HAS_TELEGRAMS)


    def test_account_not_linked_launch_request(self):
        i18n = Constants.i18n
        handler = sb.lambda_handler()
        
        # Remove access token to simulate a user who did not link account
        launch_request["context"]["System"]["user"]["accessToken"] = None
        launch_request["session"]["user"]["accessToken"] = None
        
        event = handler(launch_request, None)
        ssml = ssml = event.get('response').get('outputSpeech').get('ssml')
        self.assertEqual(ssml, '<speak>{}</speak>'.format(i18n.ACCOUNT_LINKING_REQUIRED))

    def test_account_not_authorized_launch_request(self):
        i18n = Constants.i18n
        handler = sb.lambda_handler()
        
        launch_request["context"]["System"]["user"]["accessToken"] = INVALID_TOKEN
        launch_request["session"]["user"]["accessToken"] = INVALID_TOKEN
        
        event = handler(launch_request, None)
        ssml = event.get('response').get('outputSpeech').get('ssml')
        self.assertEqual(ssml, '<speak>{}</speak>'.format(i18n.NOT_AUTHORIZED))

if __name__ == "__main__":
    set_language_model('en-US', True)
    suite = unittest.TestSuite()
    suite.addTest(LaunchIntentTest("test_authorized_launch_request"))
    suite.addTest(LaunchIntentTest("test_account_not_linked_launch_request"))
    suite.addTest(LaunchIntentTest("test_account_not_authorized_launch_request"))
    runner = unittest.TextTestRunner()
    runner.run(suite)