"""
    Definition of values
"""
# pylint: disable=C0301,C0305

from values import ValueItem

values_items_json : dict[int, ValueItem] = { 
        1: ValueItem("What cloud is used in the project?", "F_CLOUD_PROVIDER"),
        2: ValueItem("From what platform is project migrated?", "F_MIGRATE_FROM"),
        3: ValueItem("What serverless service is used in the project?","F_SERVERLESS_SERVICE"),
        4: ValueItem("What compute service (VMs, Azure Kubernetes Service) is used in the project?", "F_COMPUTE_SERVICE"),
        5: ValueItem("What hosting is used in the project?", "F_HOSTING_SERVICE"),
        6: ValueItem("What relational database is used in the project?", "F_RELATIONAL_DB_SERVICE"),
        7: ValueItem("What NoSQL is used in the project?", "F_NOSQL_SERVICE"),
        8: ValueItem("What caching is used in the project?", "F_CACHING_SERVICE"),
        9: ValueItem("What storage is used in the project?", "F_STORAGE_SERVICE")
    }


        # 1: ValueItem("What is cloud name that used by project (AWS, Azure, GCP)", "F_CLOUD_PROVIDER"),
        # 2: ValueItem("What is platform that project migrated (Azure, GCP, TIBCO, ATOS)", "F_MIGRATE_FROM"),
        # 3: ValueItem("What is serverless service used in the project (Azure Functions, Google Cloud Functions, etc.)","F_SERVERLESS_SERVICE"),
        # 4: ValueItem("What is compute service used in the project (VMs, Azure Kubernetes Service, etc.)", "F_COMPUTE_SERVICE"),
        # 5: ValueItem("What is hosting service used in the project (Azure App Service, AKS, etc.)", "F_HOSTING_SERVICE"),
        # 6: ValueItem("What is relational database service used in the project (Azure SQL, PostgreSQL, etc.)", "F_RELATIONAL_DB_SERVICE"),
        # 7: ValueItem("What is NoSQL service used in the project (Azure Cosmos DB, etc.)", "F_NOSQL_SERVICE"),
        # 8: ValueItem("What is caching service used in the project (Azure Redis Cache, etc.)", "F_CACHING_SERVICE"),
        # 9: ValueItem("What is storage service used in the project (Azure Blob Storage, File storage, etc.)", "F_STORAGE_SERVICE")
