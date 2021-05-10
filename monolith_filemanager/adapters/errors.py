

class S3ProcessesAdapterError(Exception):
    """
    This class is responsible for flagging errors in s3 processes.
    """
    def __init__(self, message: str) -> None:
        """
        The constructor for the S3ProcessesAdapterError class.

        :param message: (str) the error message raised when being called
        """
        super().__init__(message)


class LocalProcessesAdapterError(Exception):
    """
    This class is responsible for flagging errors in local processes.
    """
    def __init__(self, message: str) -> None:
        """
        The constructor for the LocalProcessesAdapterError class.

        :param message: (str) the error message raised when being called
        """
        super().__init__(message)
