class ProcessingError(Exception):

    def __init__(self, msg: str, location=None):
        if location:
            self.message = msg + f' at {location.file}:{location.line}:{location.column}'
        else:
            self.message = msg
        super().__init__(self.message)
