"""
    Value items classes
"""
# pylint: disable=C0301,C0103

from abc import ABC
from dataclasses import dataclass
from typing import List
from session_manager import BaseSessionManager
import pandas as pd

class ValueItemError(Exception):
    """ValueItem exception"""

@dataclass
class ValueItemAnswer:
    """Answer related to the value item"""
    score       : float
    answer      : str
    explanation : str
    references  : List[int]

class ValueItem:
    """
        Value item.
            question  - related question
            variable  - related variable
            answer    - answer
    """
    question    : str
    variable    : str
    answer      : ValueItemAnswer
    def __init__(self, question : str, variable : str):
        self.question = question
        self.variable = variable
        self.answer   = None

    def set_answer(self, answer : ValueItemAnswer):
        """Assign answer to the value item"""
        self.answer = answer

    def get_answer(self) -> ValueItemAnswer:
        """Get answer of the value item"""
        return self.answer

class ValueItemManager(ABC):
    """
        Manage value items
    """
    sessionManager : BaseSessionManager
    values_json : dict[int, ValueItemAnswer]
    __SESSION_NAME = 'values_manager_session'
    _value_items_data_columns = ["#", 'Value item', 'Variable']
    _value_items_values_columns= ["#", 'Value item', 'Variable', 'Answer', 'Explanation', 'References', 'Score']

    def __init__(self,  values_json : dict[int, ValueItemAnswer], sessionManager : BaseSessionManager):
        self.sessionManager = sessionManager
        self.values_json = values_json
        self.load_state()

    def load_state(self):
        """Load state from session if exists"""
        self.clear_all_answers(False)
        state : dict[int, ValueItemAnswer] = self.sessionManager.load(self.__SESSION_NAME)
        if not state:
            return
        for answer_item in state.items():
            self.set_answer(answer_item[0], answer_item[1])

    def save_state(self):
        """Save state into session"""
        state = dict[int, ValueItemAnswer]()
        for node_item in self.values_json.items():
            state[node_item[0]] = node_item[1].answer
        self.sessionManager.save(self.__SESSION_NAME, state)

    def clear_all_answers(self, save : bool = True):
        """Clear all answers and save state (if save is True)"""
        for node_item in self.values_json.items():
            node_item[1].set_answer(None)
        if save:
            self.save_state()

    def get_list_as_dataFrame(self) -> pd.DataFrame:
        """Return value items as DataFrame"""
        result = []
        for node_item in self.values_json.items():
            row = [node_item[0], node_item[1].question, node_item[1].variable]
            result.append(row)
        return pd.DataFrame(result, columns = self._value_items_data_columns)

    def get_values_as_dataFrame(self) -> pd.DataFrame:
        """Return value items as DataFrame"""
        result = []
        for node_item in self.values_json.items():
            row = [node_item[0], node_item[1].question, node_item[1].variable]
            if node_item[1].answer:
                row.extend([
                    node_item[1].answer.answer, 
                    node_item[1].answer.explanation, 
                    node_item[1].answer.references, 
                    node_item[1].answer.score
                ])
            else:
                row.extend([None, None, None, None])
            result.append(row)
        return pd.DataFrame(result, columns = self._value_items_values_columns)

    def get_list_as_numerated(self) -> str:
        result = []
        for node_item in self.values_json.items():
            result.append(f'{node_item[0]}. {node_item[1].question}')
        return '\n'.join(result)

    def __get_value_item_by_id(self, node_id : int) -> ValueItemAnswer:
        if node_id in self.values_json:
            return self.values_json[node_id]
        return None

    def set_answer(self, value_item_id : int, answer : ValueItemAnswer):
        """Set answer for value item"""
        value_item = self.__get_value_item_by_id(value_item_id)
        if not value_item:
            raise ValueItemError(f"Unknown value item {value_item_id}")
        value_item.set_answer(answer)
        self.save_state()

    def get_answer(self, value_item_id : int) -> ValueItemAnswer:
        """Get answer for value item"""
        value_item = self.__get_value_item_by_id(value_item_id)
        if not value_item:
            return None
        return value_item.get_answer()

    def get_variable_values(self) -> dict[str, bool]:
        """Get list of variables"""
        result = dict[str, bool]()
        for node_item in self.values_json.items():
            if not node_item[1].variable or  not node_item[1].answer:
                continue
            answer = node_item[1].answer.answer
            if answer is None:
                continue
            result[node_item[1].variable] = answer
        return result
