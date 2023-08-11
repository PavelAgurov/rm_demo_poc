"""
    Tests for recommendation classes.
    To run: pytest
"""
# pylint: disable=C0103,R0915,C0301

from recommendation import RecommendationManager, RecommendationItem
from session_manager import MemorySessionManager

recommendation_test_json = [
    RecommendationItem({"F_1":1}, "R-1"),
    RecommendationItem({"F_1":1, "F_2":1}, "R-2"),
    RecommendationItem({"F_3":0}, "R-3")
]

def test_recommendations():
    """Tests for recommendation full list"""
    memorySessionManager = MemorySessionManager()
    recommendationManager = RecommendationManager(recommendation_test_json, memorySessionManager)
    r_list = recommendationManager.get_full_recomendation_list()
    assert len(r_list) == 3

    recommendations = recommendationManager.get_recommendation_list({})
    assert len(recommendations) == 0

    recommendations = recommendationManager.get_recommendation_list({"F_1": 1})
    assert len(recommendations) == 1
    assert recommendations[0] == "R-1"

    recommendations = recommendationManager.get_recommendation_list({"F_1": 0})
    assert len(recommendations) == 0

    recommendations = recommendationManager.get_recommendation_list({"F_1": 1, "F_2": 1})
    assert len(recommendations) == 2
    assert recommendations[0] == "R-1"
    assert recommendations[1] == "R-2"

    recommendations = recommendationManager.get_recommendation_list({"F_3": 0})
    assert len(recommendations) == 1
    assert recommendations[0] == "R-3"

    recommendations = recommendationManager.get_recommendation_list({"F_1": None, "F_2": None})
    assert len(recommendations) == 0

    recommendations = recommendationManager.get_recommendation_list({"F_3": None})
    assert len(recommendations) == 0
