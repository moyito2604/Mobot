class ReconnectError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class AudioDownloadError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)
