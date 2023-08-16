"""
    Store all dialogs with user
"""

# pylint: disable=C0103,C0303,C0304,C0411

from datetime import datetime
import pandas as pd
from session_manager import BaseSessionManager
from dataclasses import dataclass

@dataclass
class DialogItem:
    """One item of dialog"""
    created : datetime
    question : str
    answer : str
    facts : list[str]
    error : bool

class DialogStorage:
    """Dialog storage"""
    sessionManager : BaseSessionManager
    dialog_list : list[DialogItem]
    
    _SESSION_COLLECTED_DIALOG = 'collected_dialog'
    _columns = ['Time', 'Question', 'Answer', 'Facts', 'Error']

    def __init__(self, sessionManager : BaseSessionManager):
        self.sessionManager = sessionManager
        self.load_state()

    def load_state(self):
        """load state from session"""
        self.dialog_list = self.sessionManager.load(self._SESSION_COLLECTED_DIALOG)
        if not self.dialog_list:
            self.dialog_list = list[DialogItem]()

    def save_state(self):
        """Save state into session"""
        self.sessionManager.save(self._SESSION_COLLECTED_DIALOG, self.dialog_list)

    def add_dialog(self, dialog_item : DialogItem):
        """Register dialog without error"""
        self.dialog_list.append(dialog_item)
        self.save_state()

    def get_dialog_list(self) -> list[DialogItem]:
        """Get dialog list"""
        return self.dialog_list

    def get_dialog_list_as_dataFrame(self) -> pd.DataFrame:
        """Get dialog list ad DataFrame"""
        result = []
        for data_item in self.dialog_list:
            result.append([data_item.created, data_item.question, data_item.answer, data_item.facts, data_item.error])
        return pd.DataFrame(result, columns = self._columns)

    def get_collected_fact_list(self, no_error_only : bool = True) -> list[str]:
        """Get list of facts"""
        result = []
        for data_item in self.dialog_list:
            if no_error_only and data_item.error:
                continue
            for f in data_item.facts:
                if not f.endswith('.'):
                    f+='.'
                result.append(f)
        result = list(set(result))
        return result
