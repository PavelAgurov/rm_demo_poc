# """Answer classes"""
# from dataclasses import dataclass
# from abc import abstractmethod
# from typing import List
# import pandas as pd
# import streamlit as st

# # pylint: disable=C0103

# @dataclass
# class Answer:
#     """Answer to the question"""
#     answer_id : int # usually the same as node_id
#     score : float
#     answer : str
#     explanation : str
#     references : []

# class BaseAnswerManager():
#     """Base class to manage answers"""

#     @abstractmethod
#     def save_answers(self, answer_list : List[Answer]):
#         """Save answers"""

#     @abstractmethod
#     def get_answer_by_id(self, answer_id : int) -> Answer:
#         """Return answer by id"""

#     def get_answer_value_by_id(self, answer_id : int) -> int:
#         """Return answer value by id (None/0/1)"""

#     @abstractmethod
#     def get_answers_dataFrame(self) -> pd.DataFrame:
#         """Get list of answers as DataFrame"""

#     @abstractmethod
#     def set_initial_information_provided(self):
#         """Return True if initial information was provided"""

#     @abstractmethod
#     def get_initial_information_provided(self) -> bool:
#         """Set flag that initial information was provided"""

# class AnswerManager(BaseAnswerManager):
#     """Responsible for answer handling"""

#     SESSION_COLLECTED_ANSWERS = 'collected_answers'
#     SESSION_INIT_INFO_PROVIDED = 'init_info_provided'

#     _index_column_name  = "#"
#     _answer_column_index = 2
#     _columns = [_index_column_name, 'Question', 'Answer', 'Explanation', 'References', 'Score']

#     def __init__(self):
#         super().__init__()

#         if self.SESSION_COLLECTED_ANSWERS not in st.session_state:
#             st.session_state[self.SESSION_COLLECTED_ANSWERS] = dict[int, Answer]
#         if self.SESSION_INIT_INFO_PROVIDED not in st.session_state:
#             st.session_state[self.SESSION_INIT_INFO_PROVIDED] = False

#     def save_answers(self, answer_list : List[Answer]):
#         saved_answer_dict : dict[int, Answer] = st.session_state[self.SESSION_COLLECTED_ANSWERS]
#         for answer in answer_list:
#             if not answer.answer_id in saved_answer_dict:
#                 saved_answer_dict[answer.answer_id] = None
#             saved_answer_dict[answer.answer_id] = answer

#     def get_answers_dataFrame(self) -> pd.DataFrame:
#         saved_answer_dict : dict[int, Answer] = st.session_state[self.SESSION_COLLECTED_ANSWERS]
#         if saved_answer_dict is None:
#             return None
#         result = []
#         for answer in saved_answer_dict.values():
#             result.append([answer.answer_id, question, answer.answer, answer.explanation, answer.references, answer.score])
#         return pd.DataFrame(result, columns = self._columns)

#     def get_answer_by_id(self, answer_id : int) -> Answer:
#         saved_answer_dict : dict[int, Answer] = st.session_state[self.SESSION_COLLECTED_ANSWERS]
#         if saved_answer_dict is None:
#             return None
#         if not answer_id in saved_answer_dict:
#             return None
#         return saved_answer_dict[answer_id]

#     def get_answer_value_by_id(self, answer_id : int) -> int:
#         saved_answer_dict : dict[int, Answer] = st.session_state[self.SESSION_COLLECTED_ANSWERS]
#         if saved_answer_dict is None:
#             return None
#         if not answer_id in saved_answer_dict:
#             return None
#         return saved_answer_dict[answer_id]

#     def set_initial_information_provided(self):
#         st.session_state[self.SESSION_INIT_INFO_PROVIDED] = True

#     def get_initial_information_provided(self) -> bool:
#         return st.session_state[self.SESSION_INIT_INFO_PROVIDED]
    