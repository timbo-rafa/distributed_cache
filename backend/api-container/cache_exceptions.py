
class CacheError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = args[0] if len(args) > 0 else None

    def __str__(self):
        return "Cache error: " + super().__str__()

class ApiError(CacheError):
    def __str__(self):
        return "Api error: " + Exception.__str__(self)

class MissingParameterError(ApiError):
    def __str__(self):
        return "Missing parameter error: " + Exception.__str__(self)