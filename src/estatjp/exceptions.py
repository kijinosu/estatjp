"""This module provides centralized handling of exceptions for estatjp
"""
from datetime import datetime

class estatjpError(Exception):
    """Exception for when API request url is lacking a required 'appId=' string. Ref: <https://note.com/hafnium/n/nbb6179633a5e>
    
    Derives from built-in Exception class
    
    """
    internal_err_msg = "estatjp AppIDError"
    def __init__(self, *args, user_err_msg=None):
        """
        :param args: If provided, the first argument replaces internal_err_msg.

        :param user_err_msg: If provided, replaces default message.

        """
        if args:
            self.internal_err_msg = args[0]
            super().__init__(*args)
        else:
            super().__init__(self.internal_err_msg)

        if user_err_msg is not None:
            self.user_err_msg = user_err_msg
    
    def log_exception(self):
        exception_data = {
            "type": type(self).__name__,
            "message": self.internal_err_msg,
            "args": self.args[1:],
            "notes": self.get_notes(),
            "timestamp": datetime.now(datetime.timezone.utc).isoformat()
        }
        print(f"LOG_EXCEPTION: {exception_data}")

    def get_notes(self):
        """
        Function 'get_notes`

        :return: Concatenated list of notes added with the add_note() build-in function.

        """
        li = self.__dict__.get("__notes__")
        return ' '.join(li)

class AppIDError(estatjpError):
    """
    AppIDError is raised when the API request query string lacks the 'appId=' string.
    """
    user_err_msg = "The API request url is lacking a required 'appId=' string."
    pass

class AppIDMissingError(estatjpError):
    """
    AppIDMissingError is raised whe the API ID is missing from the .env file.
    """
    user_err_msg = "The API ID is missing from the .env file."
    pass

class MissingVALUEError(estatjpError):
    """
    MissingVALUEError is raised when the response content file is missing a line starting with the string 'VALUE'.
    """
    user_err_msg = "the response content file is missing a line starting with the string 'VALUE'."
    pass
