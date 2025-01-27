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
    variables : dict[str, str]
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

    def variable_has_required_value(self, variable_name : str, required_value : str, variable_values : dict[str, str]) -> bool:
        """Check if variable has required value from variable list"""
        if variable_name not in variable_values:
            return False
        variable_value = str(variable_values[variable_name]).lower().strip()
        required_value = str(required_value).lower().strip()
        return variable_value == required_value

    def get_recommendation_list(self, variable_values : dict[str, str]) -> list[str]:
        """Get list of recommendation based on variables"""

        variable_urls = '&'.join([f'{v[0]}={v[1]}' for v in variable_values.items()])

        result = []
        for r in self._storage:
            required_variables = r.variables
            all_requred_set = True
            for v in required_variables.items():
                if not self.variable_has_required_value(v[0], v[1], variable_values):
                    all_requred_set = False
            if all_requred_set:
                result_str = r.recommendation
                result_str = result_str.replace('#VARS#', variable_urls)
                result.append(result_str)
        return result

    def get_recommendation_list_as_dataFrame(self, variable_values : dict[str, str]) -> pd.DataFrame:
        """Get list of recommendation based on variables"""
        result = self.get_recommendation_list(variable_values)
        return pd.DataFrame(result, columns=["Recommendation"])

    def get_unknown_valiable_list(self, all_variables : list[str]) -> list[str]:
        """Validate variables"""
        result = []
        for r in self._storage:
            required_variables = r.variables
            for v in required_variables.items():
                if v[0] not in all_variables:
                    result.append(v[0])
        return result
