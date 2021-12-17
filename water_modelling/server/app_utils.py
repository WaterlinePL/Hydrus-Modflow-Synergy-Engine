import os
from sys import platform
from typing import Dict

from server.user_state import UserState

if platform == "linux" or platform == "linux2" or platform == "darwin":
    PROJECT_ROOT = "../"
elif platform == "win32":
    PROJECT_ROOT = "..\\"

Cookie = str


class AppUtils:

    def __init__(self):
        self.allowed_types = ["ZIP"]
        self.project_root = os.path.abspath(PROJECT_ROOT)
        self.workspace_dir = os.path.join(self.project_root, 'workspace')
        self.user_states: Dict[Cookie, UserState] = {}

    def get_user_by_cookie(self, cookie: str):
        if cookie not in self.user_states:
            raise Exception("Unauthorized cookie used by user!")
        return self.user_states[cookie]

    def add_user(self, cookie: str):
        # Initiate singleton setup
        state = UserState()
        state.setup()
        self.user_states[cookie] = state
