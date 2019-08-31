class Error:
    __error_code = None
    __error_message = None

    def __init__(self, error_code, error_message):
        self.__error_code = error_code
        self.__error_message = error_message

    def serialize(self):
        return {
            'error_code': self.__error_code,
            'error_message': self.__error_message
        }