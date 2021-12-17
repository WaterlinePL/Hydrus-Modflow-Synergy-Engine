from __future__ import annotations

from typing import Dict, Optional
from server.user_state import UserState

Cookie = str

COOKIE_NAME = 'user_auth'
_user_states: Dict[Cookie, UserState] = {}


def get_user_by_cookie(cookie: str) -> Optional[UserState]:
    if not cookie:
        return None
    if cookie not in _user_states:
        add_user(cookie)
    return _user_states[cookie]


def add_user(cookie: str):
    state = UserState()
    state.setup()
    _user_states[cookie] = state
