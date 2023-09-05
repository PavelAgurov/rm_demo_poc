"""
    Tests for dialog storage classes.
    To run: pytest
"""

# pylint: disable=C0103,R0915,C0301,C0303,C0411

import pandas as pd
from datetime import datetime
from dialog_storage import DialogStorage, DialogItem
from session_manager import MemorySessionManager

def test_dialog_storage():
    """Test for dialog storage"""
    memorySessionManager = MemorySessionManager()
    dialogStorage = DialogStorage(memorySessionManager)

    dialog_list = dialogStorage.get_dialog_list()
    assert len(dialog_list) == 0

    # add dialog
    dialogStorage.add_dialog(DialogItem(datetime.now(), 1, "Q1", "A1", ["F1"], None, False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 1
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 1
    assert facts[0] == 'F1.' # dot added

    dialog_list = dialogStorage.get_dialog_list()
    assert len(dialog_list) == 1

    # restore dialog from session
    restoredDialogStorage = DialogStorage(memorySessionManager)
    dialog_list = restoredDialogStorage.get_dialog_list()
    assert len(dialog_list) == 1
    facts = restoredDialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 1

    # second dialog
    dialogStorage.add_dialog(DialogItem(datetime.now(), 2, "Q2", "A2", ["F2"], None, False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 2
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2

    # dialog with error
    dialogStorage.add_dialog(DialogItem(datetime.now(), 3, "Err1", "A3", ["F3"], None, True))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 3
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2
    assert 'F3.' not in facts
    facts = dialogStorage.get_collected_fact_list(no_error_only=False)
    assert len(facts) == 3
    assert 'F3.' in facts

    # duplicate facts are ignored
    dialogStorage.add_dialog(DialogItem(datetime.now(), 4, "Q4", "A4", ["F1"], None, False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 4
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2

    # answer to the same fact 2 - we should use only last fact
    dialogStorage.add_dialog(DialogItem(datetime.now(), 2, "Q2", "A21", ["F21"], 'D2', False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 5
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2
    assert 'F21.' in facts
    assert 'F2.' not in facts

    # direct answer to the question
    direct_answers = dialogStorage.get_collected_direct_answers(True)
    assert direct_answers is not None
    assert len(direct_answers) == 1
    assert direct_answers[2] == 'D2'
    
