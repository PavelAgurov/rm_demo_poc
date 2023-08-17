"""
    Data for recommendation
"""
# pylint: disable=C0304,C0305,C0301

from recommendation import RecommendationItem

recommendation_json = [
    RecommendationItem({"F_MIGRATE": 1}, "Consider Azure's migration <a href='https://azure.microsoft.com/en-us/solutions/migration?#VARS#'>services</a> for a seamless transition."),
    RecommendationItem({"F_CLOUD_PROVIDER": "Azure", "F_COMPUTE" : 1},	"Consider Azure VMs or Azure Kubernetes Service for compute needs."),
    RecommendationItem({"F_SERVERLESS_COMPUTE":1, "F_CLOUD_PROVIDER": "Azure"},	"Consider using Azure Functions for serverless compute capabilities."),
    RecommendationItem({"F_CONTAINERIZATION": 1},	"Containerization template. Consider Azure Kubernetes Service for orchestration."),
    RecommendationItem({"F_DOCKER": 1},	"Deploy using Azure Container Instances or Azure Kubernetes Service with Docker."),
    RecommendationItem({"F_DATABASE": 1, "F_RELATIONAL_DB" : 1},	"Explore Azure SQL Database or Azure Database for PostgreSQL."),
    RecommendationItem({"F_DATABASE": 1, "F_NOSQL_SERVICE" :1},	"Explore Azure Cosmos DB for NoSQL requirements."),
    RecommendationItem({"F_CACHING": 1},	"Consider using Azure Redis Cache for enhanced performance."),
    RecommendationItem({"F_STORAGE": 1},	"Explore Azure Blob Storage or Azure File Storage for data storage needs."),
    RecommendationItem({"F_MIGRATE_FROM": "GCP" , "F_CLOUD_PROVIDER": "Azure"},	"Consider strategies for transitioning from BigQuery to Azure Data Lake."),
    RecommendationItem({"F_MIGRATE_FROM": "TIBCO", "F_CLOUD_PROVIDER" : "Azure"},	"Leverage Azure's integration services for a smooth transition from TIBCO."),
    RecommendationItem({"F_MIGRATE_FROM": "ATOS", "F_CLOUD_PROVIDER" :"Azure"},	"Consider Azure DevOps and other Azure services for digital transformation.")
]

