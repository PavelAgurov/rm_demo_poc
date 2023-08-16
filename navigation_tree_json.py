"""
    Definition of treeview for navigation
"""
# pylint: disable=C0301,C0305

from navigation import TreeViewNode

tree_json : dict[int, TreeViewNode] = { # Yes/No nodes or Document name
        1:  TreeViewNode.branch_node(2, 3, "Is it migration of existed project?", "F_MIGRATE", context="Otherwise it's new project"),
        2:  TreeViewNode.question_node(4, "Does project use cloud provider?", context= "For example it can be Azure, GCP, TIBCO or ATOS"),
        3:  TreeViewNode.question_node(4, "Is the migration project?", context="For example it can be migration from Azure, GCP, TIBCO, or ATOS"),
        4:  TreeViewNode.branch_node(5, 8, "Do you require compute capabilities for project?", "F_COMPUTE"),
        5:  TreeViewNode.branch_node(6, 7, "Are you considering serverless or event-driven architectures for compute?", "F_SERVERLESS_COMPUTE"),
        6:  TreeViewNode.question_node(8, "Is the serverless service under consideration?", context="For example it can be Azure Functions, Google Cloud Functions, or another."),
        7:  TreeViewNode.question_node(8, "Is the compute service under consideration?",context="For example VMs, Azure Kubernetes Service, or another."),
        8:  TreeViewNode.branch_node(9, 12, "Is a specific hosting type being considered for the application?", "F_HOSTING_TYPE"),
        9:  TreeViewNode.branch_node(10, 11, "Is containerization a part of your hosting strategy?", "F_CONTAINERIZATION"),
        10:  TreeViewNode.question_node(12, "Are you planning to use Docker for containerization?", "F_DOCKER"),
        11:  TreeViewNode.question_node(12, "Is the hosting service under consideration Azure App Service, AKS, or another?"),
        12:  TreeViewNode.branch_node(13, 16, "Are you considering specific database services?", "F_DATABASE"),
        13:  TreeViewNode.branch_node(14, 15, "Do you require relational databases?", "F_RELATIONAL_DB"),
        14:  TreeViewNode.question_node(16, "Is the relational database service under consideration Azure SQL, PostgreSQL, or another?"),
        15:  TreeViewNode.question_node(16, "Is the NoSQL service under consideration Azure Cosmos DB or another?"),
        16:  TreeViewNode.branch_node(17, 18, "Do you require caching capabilities for your project?", "F_CACHING"),
        17:  TreeViewNode.question_node(18, "Is the caching service under consideration Azure Redis Cache or another?"),
        18:  TreeViewNode.branch_node(19, None, "Do you require storage solutions other than databases?", "F_STORAGE"),
        19:  TreeViewNode.question_node(None, "Is the storage service under consideration Azure Blob Storage, File Storage, or another"),
}

