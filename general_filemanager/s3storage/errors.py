

class BucketManagetError(Exception):

    def __init__(self, message):
        super().__init__(message)


class FileManagerError(Exception):

    def __init__(self, message):
        super().__init__(message)


class V1EngineError(Exception):

    def __init__(self, message):
        super().__init__(message)
