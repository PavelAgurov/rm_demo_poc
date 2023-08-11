"""
    Recommendations
"""
# pylint: disable=C0103,R0915,C0301,C0304

from dataclasses import dataclass
from typing import Any
import pandas as pd
from session_manager import BaseSessionManager

@dataclass
class RecommendationItem:
    """Recommendation"""
    variables : dict[str, bool]
    recommendation : str

class RecommendationManager:
    """Recommendation storage and manager"""
    _storage : list[RecommendationItem]
    sessionManager : BaseSessionManager
    def __init__(self, json : Any, sessionManager : BaseSessionManager):
        self._storage = json
        self.sessionManager = sessionManager

    def get_full_recomendation_list(self) -> list[str]:
        """Get full list of recommendation"""
        result = []
        for r in self._storage:
            variable_str = ', '.join([f'{v[0]}:{v[1]}' for v in r.variables.items()])
            result.append([variable_str, r.recommendation])
        return result
    
    def get_full_recomendation_list_as_dataFrame(self) -> pd.DataFrame:
        """Get full list of recommendation as DataFrame"""
        result = self.get_full_recomendation_list()
        return pd.DataFrame(result, columns=["Variables", "Recommendation"])

    def variable_has_required_value(self, variable_name, required_value, variable_values : dict[str, bool]) -> bool:
        """Check if variable has required value from variable list"""
        if not variable_name in variable_values:
            return False
        variable_value = variable_values[variable_name]
        return variable_value == required_value

    def get_recommendation_list(self, variable_values : dict[str, bool]) -> list[str]:
        """Get list of recommendation based on variables"""
        result = []
        for r in self._storage:
            required_variables = r.variables
            all_requred_set = True
            for v in required_variables.items():
                if not self.variable_has_required_value(v[0], v[1], variable_values):
                    all_requred_set = False
            if all_requred_set:
                result.append(r.recommendation)
        return result

    def get_recommendation_list_as_dataFrame(self, variable_values : dict[str, bool]) -> pd.DataFrame:
        """Get list of recommendation based on variables"""
        result = self.get_recommendation_list(variable_values)
        return pd.DataFrame(result, columns=["Recommendation"])

