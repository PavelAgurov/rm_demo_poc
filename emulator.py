"""
    LLM Emulator
"""
# pylint: disable=C0103,C0301

from classes import FactList
from navigation import Answer, TreeDialogNavigator

LLM_EMULATOR_INFO_HTML = "<p>LLM Emulation answers: <i>FACT:YES1</i> - answer yes for question 1, <i>FACT:NO2</i> - answer no for question 2, ERR - error</p>"

def EMULATOR_get_fact_list(node_id : int, provied_answer : str) -> FactList:
    """Fact list extractor emulator"""
    error_emulation = provied_answer[0].lower() == "e"
    if provied_answer.startswith("FACT:"):
        return FactList([provied_answer.removeprefix("FACT:")], error_emulation)
    return FactList([f"{node_id}-1", f"{node_id}-2"], error_emulation)

def EMULATOR_set_answers(fact_list_str : str, dialog_navigator : TreeDialogNavigator):
    """Answer list extractor emulator"""
    for fact in fact_list_str.split('\n'):
        i = fact.find("YES")
        if i > 0:
            fact = fact[i+3:].strip()
            if fact.isnumeric():
                dialog_navigator.set_node_answer(int(fact), Answer(1, True , "", []))
        i = fact.find("NO")
        if i > 0:
            fact = fact[i+2:].strip()
            if fact.isnumeric():
                dialog_navigator.set_node_answer(int(fact), Answer(0, False , "", []))
