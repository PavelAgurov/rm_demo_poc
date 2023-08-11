"""
    Work with sessions
"""
from abc import abstractmethod
from typing import Any
import streamlit as st

class BaseSessionManager():
    """Base class for session manager"""
    @abstractmethod
    def save(self, name : str, obj : Any):
        """Save object into session"""

    @abstractmethod
    def load(self, name : str) -> Any:
        """Load object from session"""

class StreamlitSessionManager(BaseSessionManager):
    """Session manager to save/load objects"""

    def save(self, name : str, obj : Any):
        st.session_state[name] = obj

    def load(self, name : str) -> Any:
        if not name in st.session_state:
            return None
        return st.session_state[name]

class MemorySessionManager(BaseSessionManager):
    """Session manager to save/load objects"""
    _storage : dict[str, str]

    def __init__(self):
        self._storage = dict[str, Any]()

    def save(self, name : str, obj : Any):
        self._storage[name] = obj

    def load(self, name : str) -> Any:
        if not name in self._storage:
            return None
        return self._storage[name]
