"""
    Definition of treeview for navigation
"""
# pylint: disable=C0301,C0305

from navigation import TreeViewNode

tree_json : dict[int, TreeViewNode] = { # Yes/No nodes or Document name
        1: TreeViewNode.branch_node(2, 3, "Is it migration of existed project?", "F_MIGRATION"),
        2: TreeViewNode.question_node(3, "Should project use cloud provider for example Azure, GCP, TIBCO, ATOS?", "F_CLOUD"),
        3: TreeViewNode.question_node(4, "Can project be containerized?", "F_CONTAINERIZED"),
        4: TreeViewNode.branch_node(5, 8, "Has project API?", "F_HAS_API"),
        5: TreeViewNode.question_node(6, "Do you use RestAPI?", "F_REST_API"),
        6: TreeViewNode.branch_node(7, 8, "Is it exactly external API?", "F_EXT_API"),
        7: TreeViewNode.question_node(8, "Do you want to monetize your API?", "F_API_MONEY"),
        8: TreeViewNode.branch_node(9, None, "Do you use database?", None),
        9: TreeViewNode.branch_node(None, 10, "Do you use relation database?", "F_REL_DB"),
        10: TreeViewNode.question_node(None, "Do you use noSQL?", "F_NOSQL"),

        100: TreeViewNode.question_node(None, "Do you have caching in your application?", "F_CACHE"),
        101: TreeViewNode.question_node(None, "Do you use Redis?", "F_REDIS")
    }

