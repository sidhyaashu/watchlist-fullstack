from enum import Enum


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AuthProviderEnum(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    BOTH = "both"


class OTPTypeEnum(str, Enum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"
    SETUP_PASSWORD = "setup_password"


class AnalyticsEventTypeEnum(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    ACCOUNT_DELETE = "account_delete"
