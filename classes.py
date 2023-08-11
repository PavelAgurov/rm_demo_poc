"""
    Class definitions
"""
from dataclasses import dataclass

@dataclass
class CurrentQuestion:
    """
        Current question 
            - nodeid (if it's already dialog)
            - current_question - question
            - displayed_message - what we should to the user
    """
    dialog_node_id : int
    current_question : str
    displayed_message : str

@dataclass
class FactList:
    """
        Fact list
    """
    facts : list[str]
    error : bool