"""
    Tests for navigation classes.
    To run: pytest
"""
from navigation import TreeDialogNavigator, TreeViewNode, Answer
from session_manager import MemorySessionManager

# pylint: disable=C0103,R0915,C0301

tree_json_for_test : dict[int, TreeViewNode] = { # Yes/No nodes or Document name
        1: TreeViewNode.branch_node(2, 3, "N1", "F_N1"),
        2: TreeViewNode.question_node(3, "N2", "F_N2"),
        3: TreeViewNode.question_node(4, "N3", None),
        4: TreeViewNode.branch_node(5, 8, "N4", "F_N4"),
        5: TreeViewNode.question_node(6, "N5", "F_N5"),
        6: TreeViewNode.branch_node(7, 8, "N6", "F_N6"),
        7: TreeViewNode.question_node(8, "N7", "F_N7"),
        8: TreeViewNode.branch_node(9, None, "N8", "F_N8"),
        9: TreeViewNode.branch_node(10, None, "N9", "F_N9"),
        10: TreeViewNode.question_node(None, "N10", "F_N10")
    }

def test_navigation_question_list():
    """Test for get_numerated_question_list"""
    memorySessionManager = MemorySessionManager()
    treeDialogNavigator = TreeDialogNavigator(tree_json_for_test, memorySessionManager)

    # simple question list
    question_list : [] = treeDialogNavigator.get_question_list_as_numerated().split('\n')
    assert question_list[0] == "1. N1"
    assert question_list[9] == "10. N10"

    # include answers
    question_list : [] = treeDialogNavigator.get_question_list_as_numerated(include_answer=True).split('\n')
    assert question_list[0] == "1. N1 [None]"
    assert question_list[9] == "10. N10 [None]"

    # include answers
    treeDialogNavigator.set_node_answer(1, Answer(1, True, "E1", [1, 3]))
    question_list : [] = treeDialogNavigator.get_question_list_as_numerated(include_answer=True).split('\n')
    assert question_list[0] == "1. N1 [True]"
    assert question_list[9] == "10. N10 [None]"

def test_navigation_tree():
    """"Test for navigation by tree"""

    memorySessionManager = MemorySessionManager()
    treeDialogNavigator = TreeDialogNavigator(tree_json_for_test, memorySessionManager)

    next_node_id = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 1

    # set answer
    treeDialogNavigator.set_node_answer(1, Answer(1, True, "E1", [1, 3]))
    a1 = treeDialogNavigator.get_node_answer(1)
    assert a1 is not None
    assert a1.score == 1
    assert a1.answer is True
    assert a1.explanation == "E1"
    assert a1.references == [1, 3]
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 2
    variable_list = treeDialogNavigator.get_variable_values()
    assert len(variable_list) == 1
    assert variable_list["F_N1"] is True

    # restore from session
    restoredTreeDialogNavigator = TreeDialogNavigator(tree_json_for_test, memorySessionManager)
    a1 = restoredTreeDialogNavigator.get_node_answer(1)
    assert a1 is not None
    assert a1.score == 1
    assert a1.answer is True
    assert a1.explanation == "E1"
    assert a1.references == [1, 3]
    next_node_id : int = restoredTreeDialogNavigator.get_next_nodeId()
    assert next_node_id == 2
    variable_list = treeDialogNavigator.get_variable_values()
    assert len(variable_list) == 1
    assert variable_list["F_N1"] is True

    # clean up
    treeDialogNavigator.clear_all_answers()


    treeDialogNavigator.set_node_answer(1, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 3
    variable_list = treeDialogNavigator.get_variable_values()
    assert len(variable_list) == 1
    assert variable_list["F_N1"] is False

    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(2, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 4
    variable_list = treeDialogNavigator.get_variable_values()
    assert len(variable_list) == 2
    assert variable_list["F_N1"] is True
    assert variable_list["F_N2"] is True

    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(0, False, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 4
    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(0, False, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 4
    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(1, Answer(0, False, "", []))
    treeDialogNavigator.set_node_answer(4, Answer(0, False, "", []))
    treeDialogNavigator.set_node_answer(8, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id is None
    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(2, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(8, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(9, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(4, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id == 10
    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(2, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(8, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(9, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(10, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(4, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id is None
    treeDialogNavigator.clear_all_answers()

    treeDialogNavigator.set_node_answer(1, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(2, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(3, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(8, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(9, Answer(1, True, "", []))
    treeDialogNavigator.set_node_answer(4, Answer(0, False, "", []))
    treeDialogNavigator.set_node_answer(10, Answer(0, False, "", []))
    next_node_id : int = treeDialogNavigator.get_next_nodeId()
    assert next_node_id is None
    treeDialogNavigator.clear_all_answers()
