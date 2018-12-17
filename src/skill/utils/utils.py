from html.parser import HTMLParser

from ask_sdk_model import Intent
from ask_sdk_model.dialog import ElicitSlotDirective
from six import PY3

from src.skill.i18n.language_model import LanguageModel
from src.skill.services.telethon_service import TelethonService
from src.skill.utils.exceptions import TelethonException, handle_telethon_error_response


############## PARSER ##############
def convert_speech_to_text(ssml_speech):
    """
    Converts ssml speech to text, by removing html tags
    
    Arguments:
        ssml_speech {String} -- Spoken text with ssml tags.
    
    Returns:
        [String] -- Spoken text without ssml tags.
    """
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


class SSMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.full_str_list = []
        if PY3:
            self.strict = False
            self.convert_charrefs = True

    def handle_data(self, d):
        self.full_str_list.append(d)

    def get_data(self):
        return ''.join(self.full_str_list)


def handle_authorization(handler_input):
    """
    Handles the authorization process:
    1. User entered telephone number on my server
    2. User starts Alexa skill and receives code
    3. User says retrieved code to Alexa
    4. User gets signed in and is now authorized.

    Phone code hash is used for Telegram API, because seperate instances 
    of Telethon request code and sign user in.
    
    Arguments:
        handler_input {ask_sdk_core.handler_input.HandlerInput} -- Provided by Amazon's SDK.

    Returns:
        handler_input {ask_sdk_core.handler_input.HandlerInput} -- Provided by Amazon's SDK.
    """
    i18n = LanguageModel(handler_input.request_envelope.request.locale)
    telethon_service = TelethonService()
    sess_attrs = handler_input.attributes_manager.session_attributes
    account = sess_attrs.get("ACCOUNT")
    slots = handler_input.request_envelope.request.intent.slots
    reprompt = None

    if not account.get("PHONE_NUMBER"):
        speech_text = i18n.NO_PHONE
        should_end = True
    elif not slots.get("code").value:
        try:
            phone_code_hash = telethon_service.send_code_request()
        except TelethonException as error:
            return handle_telethon_error_response(error, handler_input)

        sess_attrs["PHONE_CODE_HASH"] = phone_code_hash

        updated_intent = Intent("CustomYesIntent", slots)
        elicit_directive = ElicitSlotDirective(updated_intent, "code")
        handler_input.response_builder.add_directive(elicit_directive)

        speech_text = i18n.WHAT_IS_CODE
        reprompt = i18n.WHAT_IS_CODE_REPROMPT
        should_end = False
    else:
        phone_code_hash = sess_attrs.get("PHONE_CODE_HASH")
        try:
            ok = telethon_service.sign_user_in(slots.get("code").value, phone_code_hash)
        except TelethonException as error:
            return handle_telethon_error_response(error, handler_input)

        if ok:
            sess_attrs["ACCOUNT"]["AUTHORIZED"] = True
            speech_text = i18n.AUTHORIZED
            reprompt = i18n.FALLBACK
            should_end = False
        else:
            speech_text = i18n.WRONG_CODE
            should_end = True

    handler_input.response_builder.speak(speech_text) \
        .set_should_end_session(should_end)
    if reprompt:
        handler_input.response_builder.ask(reprompt)
    return handler_input
