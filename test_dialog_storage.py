"""
    Tests for dialog storage classes.
    To run: pytest
"""

# pylint: disable=C0103,R0915,C0301,C0411

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
    dialogStorage.add_dialog(DialogItem(datetime.now(), "Q1", "A1", ["F1"], False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 1
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 1

    dialog_list = dialogStorage.get_dialog_list()
    assert len(dialog_list) == 1

    # restore dialog from session
    restoredDialogStorage = DialogStorage(memorySessionManager)
    dialog_list = restoredDialogStorage.get_dialog_list()
    assert len(dialog_list) == 1
    facts = restoredDialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 1

    # second dialog
    dialogStorage.add_dialog(DialogItem(datetime.now(), "Q2", "A2", ["F2"], False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 2
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2

    # dialog with error
    dialogStorage.add_dialog(DialogItem(datetime.now(), "Err1", "A3", ["F3"], True))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 3
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2
    facts = dialogStorage.get_collected_fact_list(no_error_only=False)
    assert len(facts) == 3

    # duplicate facts are ignored
    dialogStorage.add_dialog(DialogItem(datetime.now(), "Q4", "A4", ["F1"], False))
    df : pd.DataFrame = dialogStorage.get_dialog_list_as_dataFrame()
    assert df is not None
    assert len(df) == 4
    facts = dialogStorage.get_collected_fact_list(no_error_only=True)
    assert len(facts) == 2
