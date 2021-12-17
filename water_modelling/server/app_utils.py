from __future__ import annotations

# from typing import TYPE_CHECKING

import os
from sys import platform
from typing import Dict, Optional

# if TYPE_CHECKING:
from server.user_state import UserState

Cookie = str


class AppUtils:
    COOKIE_NAME = 'user_auth'

    def __init__(self):
        self.user_states: Dict[Cookie, UserState] = {}

    def get_user_by_cookie(self, cookie: str) -> Optional[UserState]:
        if not cookie:
            return None
        if cookie not in self.user_states:
            raise Exception("Unauthorized cookie used by user!")
        return self.user_states[cookie]

    def add_user(self, cookie: str):
        state = UserState()
        state.setup()
        self.user_states[cookie] = state


# Initiate singleton setup
app_utils = AppUtils()
