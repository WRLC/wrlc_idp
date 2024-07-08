import unicodedata
from flask_security import username_util
from flask_security.utils import get_message


class UsernameUtil(username_util.UsernameUtil):
    def check_username(self, username: str) -> str | None:
        cats = [unicodedata.category(c)[0] for c in username]
        if any([cat not in ["L", "N", "P", "S"] for cat in cats]):
            return get_message("USERNAME_DISALLOWED_CHARACTERS")[0]
        return None
