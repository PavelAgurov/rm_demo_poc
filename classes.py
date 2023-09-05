"""
    Class definitions
"""
# pylint: disable=C0103,C0303,C0304,C0411

from dataclasses import dataclass

@dataclass
class CurrentQuestion:
    """
        Current question 
            - nodeid (if it's already dialog)
            - current_question - question
            - displayed_message - what we should to the user
    """
    dialog_node_id    : int
    current_question  : str
    displayed_message : str

@dataclass
class ExtratedFactList:
    """
        Fact list extracted from dialogs
    """
    facts         : list[str]
    direct_answer : str
    error         : bool