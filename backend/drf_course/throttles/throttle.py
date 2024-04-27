from rest_framework.throttling import UserRateThrottle


class UserBurstRateThrottle(UserRateThrottle):
    """
    To limit/throttle request rate per hour
    """
    scope = "burst"


class UserSustainedRateThrottle(UserRateThrottle):
    """
    throttle and limit rate on a per day basis
    """
    scope = "sustained"