"""
    Data for recommendation
"""
# pylint: disable=C0304,C0305,C0301

from recommendation import RecommendationItem

recommendation_json = [
    RecommendationItem({"F_CONTAINERIZED":1}, "Please read How to use Docker.docx"),
    RecommendationItem({"F_REST_API":1}, "See how to use RestAPI.pdf"),
    RecommendationItem({"F_REST_API":1, "F_API_MONEY":1}, "Monitization with RestAPI.pdf"),
    RecommendationItem({"F_REL_DB":1}, "Important to follow instruction from Security of databases"),
    RecommendationItem({"F_CACHE":1}, "Cache recommendation here"),
    RecommendationItem({"F_CLOUD_PROVIDER": "AZURE"}, "Read about Azure")
]

