"""
    Navigation classes
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from session_manager import BaseSessionManager
import pandas as pd
import graphviz
from graphviz import Digraph

class NavigationError(Exception):
    """Dialog Navigation exception"""

@dataclass
class TreeNodeAnswer:
    """Answer related to the node"""
    score       : float
    answer      : bool
    explanation : str
    references  : List[int]

class TreeViewNode:
    """
        Navigation node.
            yes_node_id - redirect if "yes"
            no_node_id  - redirect if "no"
            question    - related question
            variable    - related variable
    """
    yes_node_id : int
    no_node_id  : int
    question    : str
    variable    : str
    fixed_value : bool
    answer      : TreeNodeAnswer
    def __init__(self, yes_node_id : int, no_node_id: int, question : str, variable : str, fixed_value : bool):
        self.yes_node_id = yes_node_id
        self.no_node_id  = no_node_id
        self.question    = question
        self.variable    = variable
        self.fixed_value = fixed_value
        self.answer      = None

    @classmethod
    def branch_node(cls, yes_question_id : int, no_question_id: int, question : str, variable : str = None):
        """Create branch node - redirect depends on yes/no"""
        if question is None:
             raise NavigationError("Question can't be None for branch_node")
        return TreeViewNode(yes_question_id, no_question_id, question, variable, None)

    @classmethod
    def question_node(cls, next_node : int, question : str, variable : str = None):
        """Create question node - it's only question and one path to redirect"""
        if question is None:
             raise NavigationError("Question can't be None for question_node")
        return TreeViewNode(next_node, next_node, question, variable, None)

    @classmethod
    def fixed_node(cls, yes_question_id : int, no_question_id: int, question : str, variable : str, fixed_value : bool):
        """Create fixed value node - redirect depends on yes/no, but only if we have required answer"""
        if fixed_value is None:
             raise NavigationError("fixed_value can't be None for fixed_node")
        return TreeViewNode(yes_question_id, no_question_id, question, variable, fixed_value)

    def set_answer(self, answer : TreeNodeAnswer):
        """Assign answer to the node"""
        self.answer = answer

    def get_answer(self) -> TreeNodeAnswer:
        """Get answer of the node"""
        return self.answer

class BaseDialogNavigator(ABC):
    """
        Base class for navigation
        The main goal is to return next nodeId based on provided answers.
    """
    name : str
    sessionManager : BaseSessionManager
    def __init__(self, name : str, sessionManager : BaseSessionManager):
        self.name = name
        self.sessionManager = sessionManager
        self.load_state()

    @abstractmethod
    def load_state(self):
        """Load state from session if exists"""

    @abstractmethod
    def save_state(self):
        """Save state into session"""

    @abstractmethod
    def get_question_list_as_numerated(self, include_answer : bool = False) -> str:
        """Retun list of questions"""
        return ""

    @abstractmethod
    def get_question_list_as_dataFrame(self) -> pd.DataFrame:
        """Retun list of questions as DataFrame"""
        return None

    @abstractmethod
    def get_next_nodeId(self) -> int:
        """Return next nodeId"""
        return None

    @abstractmethod
    def get_question_by_nodeId(self, node_id) -> str:
        """Return question by nodeId"""
        return None

class TreeDialogNavigator(BaseDialogNavigator):
    """Dialog based on treeview"""
    
    tree_json : dict[int, TreeViewNode]
    __SESSION_NAME = 'tree_dialog_session'

    _question_list_columns = ["#", 'Question', 'Answer', 'Explanation', 'References', 'Score']
    _question_data_columns = ["#", 'Question', 'Yes', 'No', 'Variable']

    def __init__(self, tree_json : dict[int, TreeViewNode], sessionManager : BaseSessionManager):
        self.tree_json = tree_json
        super().__init__("TreeView", sessionManager)

    def load_state(self):
        self.clear_all_answers(False)
        state : dict[int, TreeNodeAnswer] = self.sessionManager.load(self.__SESSION_NAME)
        if not state:
            return
        for answer_item in state.items():
            self.set_node_answer(answer_item[0], answer_item[1])

    def save_state(self):
        state = dict[int, TreeNodeAnswer]()
        for node_item in self.tree_json.items():
            state[node_item[0]] = node_item[1].answer
        self.sessionManager.save(self.__SESSION_NAME, state)

    def __bool2YesNo(self, b : bool) -> str:
        if b is None:
            return None
        if b:
            return "Yes"
        return "No"

    def get_question_list_as_numerated(self, include_answer : bool = False) -> str:
        result = []
        for node_item in self.tree_json.items():
            s = f'{node_item[0]}. {node_item[1].question}'
            if include_answer:
                if node_item[1].answer:
                    s = f'{s} [{node_item[1].answer.answer}]'
                else:
                    s = f'{s} [{None}]'
            result.append(s)
        return '\n'.join(result)

    def get_question_list_as_dataFrame(self) -> pd.DataFrame:
        result = []
        for node_item in self.tree_json.items():
            row = [node_item[0], node_item[1].question]
            if node_item[1].answer:
                row.extend([
                    self.__bool2YesNo(node_item[1].answer.answer), 
                    node_item[1].answer.explanation, 
                    node_item[1].answer.references, 
                    node_item[1].answer.score
                ])
            else:
                row.extend([None, None, None, None])
            result.append(row)
        return pd.DataFrame(result, columns = self._question_list_columns)

    def __get_node_by_id(self, node_id : int) -> TreeViewNode:
        if node_id in self.tree_json:
            return self.tree_json[node_id]
        return None

    def set_node_answer(self, node_id : int, answer : TreeNodeAnswer):
        """Set answer for node"""
        node = self.__get_node_by_id(node_id)
        if not node:
            raise NavigationError(f"Unknown nodeId {node_id}")
        node.set_answer(answer)
        self.save_state()

    def get_node_answer(self, node_id : int) -> TreeNodeAnswer:
        """Get answer for node"""
        node = self.__get_node_by_id(node_id)
        if not node:
            return None
        return node.get_answer()

    def clear_all_answers(self, save : bool = True):
        """Clear all answers and save state (if save is True)"""
        for node_item in self.tree_json.items():
            node_item[1].set_answer(None)
        if save:
            self.save_state()

    def get_next_nodeId(self) -> int:
        node_id = 1
        for _ in range(10000): # just to make cycle limited
            node = self.__get_node_by_id(node_id)
            if not node:
                raise NavigationError(f"Unknown nodeId {node_id}")
            node_answer = node.get_answer()
            no_answer_yet = node_answer is None or node_answer.answer is None # no answer yet
            fixed_value = node.fixed_value
            if fixed_value is None: # it's normal node
                if no_answer_yet: 
                    return node_id
                if node_answer.answer: # we have answer yes or no
                    next_nodeId = node.yes_node_id
                else:
                    next_nodeId = node.no_node_id
            else: # fixed value node
                if no_answer_yet: # no answer yet - we will not run fixed_value branch and run opposite
                    if fixed_value:
                        next_nodeId = node.no_node_id
                    else:
                        next_nodeId = node.yes_node_id                
                else:
                    if node_answer.answer != fixed_value: # we have answer, but it's not fixed_answer - run opposite branch
                        if fixed_value:
                            next_nodeId = node.no_node_id
                        else:
                            next_nodeId = node.yes_node_id
                    else: # we have required fixed value - run related branch
                        if fixed_value:
                            next_nodeId = node.yes_node_id
                        else:
                            next_nodeId = node.no_node_id
            if not next_nodeId: # no next node, that's end of navigation
                return None
            node_id = next_nodeId
        raise NavigationError("Cycled dialog tree")

    def get_question_by_nodeId(self, node_id) -> str:
        node = self.__get_node_by_id(node_id)
        if not node:
            raise NavigationError(f"Unknown nodeId {node_id}")
        return node.question

    def get_variable_values(self) -> dict[str, bool]:
        """Get list of variables"""
        result = dict[str, bool]()
        for node_item in self.tree_json.items():
            if not node_item[1].variable or  not node_item[1].answer:
                continue
            answer_bool = node_item[1].answer.answer
            if answer_bool is None:
                continue
            result[node_item[1].variable] = answer_bool
        return result
            
    def get_tree_as_dataFrame(self) -> pd.DataFrame:
        """Return tree as DataFrame"""
        result = []
        for node_item in self.tree_json.items():
            row = [node_item[0], node_item[1].question, node_item[1].yes_node_id, node_item[1].no_node_id, node_item[1].variable]
            result.append(row)
        return pd.DataFrame(result, columns = self._question_data_columns)

    def get_dialog_graph(self, render_into_png) -> Digraph:
        """
            Return dialog graph
        """
        # Create a graphlib graph object
        graph = graphviz.Digraph(
            format = 'png'
        )
        
        has_start = False
        for node_item in self.tree_json.items():
            node_id = node_item[0]
            node = node_item[1]

            if not has_start:
                graph.edge('START', f'[{node_id}] {node.question}')
                has_start = True

            if node.yes_node_id:
                yes_node = self.__get_node_by_id(node.yes_node_id)
                graph.edge(f'[{node_id}] {node.question}', f'[{node.yes_node_id}] {yes_node.question}', "yes")
            if node.no_node_id:
                no_node = self.__get_node_by_id(node.no_node_id)
                graph.edge(f'[{node_id}] {node.question}', f'[{node.no_node_id}] {no_node.question}', "no")

        if render_into_png:
            graph.render(format='png')              
        return graph