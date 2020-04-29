class WarnValueError(ValueError):
    """Error used when the supplied value is invalid but we can continue"""
    pass


class KillValueError(ValueError):
    """Error used when the supplied value is invalid and we must STOP"""
    pass
