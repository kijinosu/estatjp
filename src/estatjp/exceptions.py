"""This module provides centralized handling of exceptions for estatjp
"""
from datetime import datetime

class AppIDError(Exception):
    """Exception for when API request url is lacking a required 'appId=' string. Ref: <https://note.com/hafnium/n/nbb6179633a5e>
    
    Derives from built-in Exception class
    
    """
    internal_err_msg = "estatjp AppIDError"
    user_err_msg = "The API request url is lacking a required 'appId=' string."

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

        :return: Concatenated list of added notes

        """
        li = self.__dict__.get("__notes__")
        return ' '.join(li)


