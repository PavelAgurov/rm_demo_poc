"""
    Main APP and UI
"""
# pylint: disable=C0301,C0103,C0411,C0303, C0305

from datetime import datetime
import json
import os

import streamlit as st

import langchain
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.cache import SQLiteCache
from langchain.callbacks import get_openai_callback

from dialog_storage import DialogStorage, DialogItem
from prompts import extract_facts_prompt_template, score_prompt_template
from utils import get_numerated_list_string, get_fixed_json
from navigation import Answer, TreeDialogNavigator
from dialog_tree_json import tree_json
from session_manager import StreamlitSessionManager
from strings import HOW_IT_WORKS, APP_HEADER, INITIAL_INFO_MESSAGE, ADDITIONAL_INFO_MESSAGE
from classes import CurrentQuestion, FactList
from utils_streamlit import streamlit_hack_remove_top_space
from emulator import EMULATOR_get_fact_list, EMULATOR_set_answers, LLM_EMULATOR_INFO_HTML
from recommendation import RecommendationManager
from recommendation_json import recommendation_json
# --------------------------------- Setup

LLM_EMULATOR = False

# --------------------------------- Sessions

SESSION_SAVED_USER_INPUT = 'saved_user_input'
SESSION_TOKEN_COUNT = 'token_count'
SESSION_INIT_INFO_PROVIDED = 'init_info_provided'

if SESSION_SAVED_USER_INPUT not in st.session_state:
    st.session_state[SESSION_SAVED_USER_INPUT] = ""
if SESSION_TOKEN_COUNT not in st.session_state:
    st.session_state[SESSION_TOKEN_COUNT] = 0
if SESSION_INIT_INFO_PROVIDED not in st.session_state:
    st.session_state[SESSION_INIT_INFO_PROVIDED] = False

def submit_user_input():
    """Save user input and clear intputbox"""
    s : str = st.session_state.user_input
    s = s.strip()
    st.session_state[SESSION_SAVED_USER_INPUT] = s
    st.session_state.user_input = ""

# ------------------------------- UI
st.set_page_config(page_title= APP_HEADER, layout="wide")
st.title(APP_HEADER)

recommendation_container = st.container().empty()

streamlit_hack_remove_top_space()

tab_main, tab_apikey, tab_data, tab_debug = st.tabs(["Request", "Settings", "Data", "Debug"])
with tab_main:
    header_container     = st.container()
    if LLM_EMULATOR:
        emulator_container = st.empty()
    question_container   = st.empty()
    input_container      = st.container()
    input_container.text_area("Your answer or request: ", "", key="user_input", on_change= submit_user_input)
    status_container     = st.empty()
    explanations_container = st.expander(label="Explanations").empty()
    debug_container      = st.container()

with tab_apikey:
    key_header_container   = st.container()
    open_api_key = key_header_container.text_input("OpenAPI Key: ", "", key="open_api_key")

with tab_data:
    navigation_data_container = st.expander(label="Navigation data").empty()
    recommendation_data_container = st.expander(label="Recommendations").empty()

with tab_debug:
    facts_from_dialog_conteiner = st.expander(label="Fact JSON").empty()
    score_result_container = st.expander(label="Score JSON").empty()
    variable_list_container = st.expander(label="Calculated variables").empty()

with st.sidebar:
    collected_dialog_container = st.expander(label="Saved dialog").empty()
    collected_facts_container  = st.expander(label="Facts", expanded=True).empty()
    token_count_container      = st.empty()

header_container.markdown(HOW_IT_WORKS, unsafe_allow_html=True)

#------------------------------- Functions

def get_current_question() -> CurrentQuestion:
    """
        Get current question
    """
    # check if we should ask initial info
    initial_info_provided = st.session_state[SESSION_INIT_INFO_PROVIDED]
    if not initial_info_provided: # we should ask initial information our of dialog
        return CurrentQuestion(None, None, INITIAL_INFO_MESSAGE)

    # check dialog
    dialog_node_id = dialog_navigator.get_next_nodeId() 
    if dialog_node_id: # it's not end of dialog yet
        question = dialog_navigator.get_question_by_nodeId(dialog_node_id)
        message = f'[{dialog_node_id}] {question}'
        return CurrentQuestion(dialog_node_id, question, message)

    # end of dialog
    return CurrentQuestion(None, None, ADDITIONAL_INFO_MESSAGE)

def get_fact_list_from_question_answer(node_id : int, question : str, provied_answer : str) -> FactList:
    """
        Get facts extracted from question and answer
    """
    if LLM_EMULATOR:
        return EMULATOR_get_fact_list(node_id, provied_answer)

    # use real LLM
    facts_from_dialog = None
    status_container.markdown('Starting LLM to extract facts...')
    with get_openai_callback() as cb:
        facts_from_dialog = extract_facts_chain.run(question = question, answer = provied_answer)
    st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
    status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
    facts_from_dialog_conteiner.markdown(facts_from_dialog)

    error = False
    fact_list_from_a2q = []
    try:
        facts_from_dialog_json = json.loads(get_fixed_json(facts_from_dialog))['it_project_facts']
        fact_list_from_a2q = [f['fact'] for f in facts_from_dialog_json]
    except: # pylint: disable=W0718,W0702
        error = True
    return FactList(fact_list_from_a2q, error)

def get_anser_value(answer_str : str) -> bool:
    """Convert answer string into bool or None"""
    answer_str = answer_str.lower()
    if answer_str == "yes":
        return 1
    if answer_str == "no":
        return 0
    return None


def extract_answers_from_fact_list(question_list_str : str, fact_list_str : str):
    """Extract answers from fact list"""

    if LLM_EMULATOR:
        EMULATOR_set_answers(fact_list_str, dialog_navigator)
        return

    status_container.markdown('Starting LLM to extract answers...')
    with get_openai_callback() as cb:
        score_result = score_chain.run(questions = question_list_str, facts = fact_list_str)
    st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
    status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
    score_result_container.markdown(score_result)

    try:
        score_result_json = json.loads(get_fixed_json(score_result))
        for answer_json in score_result_json:
            question_id  = int(answer_json["QuestionID"])
            answer_value = get_anser_value(answer_json["Answer"])
            answer = Answer(answer_json["Score"], answer_value, answer_json["Explanation"], answer_json["RefFacts"])
            dialog_navigator.set_node_answer(question_id, answer)
    except Exception as error: # pylint: disable=W0718,W0702
        explanations_container.markdown(f'Error parsing answer. JSON:\n{score_result}\n\n{error}')

#------------------------------- LLM setup

if open_api_key:
    LLM_OPENAI_API_KEY = open_api_key
else:
    LLM_OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

langchain.llm_cache = SQLiteCache()

llm = ChatOpenAI(model_name = "gpt-3.5-turbo", openai_api_key = LLM_OPENAI_API_KEY, max_tokens = 1000, temperature = 0)

extract_facts_prompt = PromptTemplate.from_template(extract_facts_prompt_template)
extract_facts_chain  = LLMChain(llm=llm, prompt = extract_facts_prompt)
score_prompt = PromptTemplate.from_template(score_prompt_template)
score_chain  = LLMChain(llm=llm, prompt = score_prompt)

if LLM_EMULATOR:
    emulator_container.markdown(LLM_EMULATOR_INFO_HTML, unsafe_allow_html=True)

#------------------------------- APP

session_manager  = StreamlitSessionManager()
dialog_storage   = DialogStorage(session_manager)
dialog_navigator = TreeDialogNavigator(tree_json, session_manager)
recommendation_manager = RecommendationManager(recommendation_json, session_manager)

current_question = get_current_question()
question_container.markdown(current_question.displayed_message)

user_input : str = st.session_state[SESSION_SAVED_USER_INPUT]
if user_input:
    extracted_fact_list = get_fact_list_from_question_answer(
                                current_question.dialog_node_id, 
                                current_question.current_question, 
                                user_input)

    # save dialog in the storage
    dialog_storage.add_dialog(DialogItem(
                    datetime.now(), 
                    current_question.current_question, 
                    user_input, 
                    extracted_fact_list.facts, 
                    extracted_fact_list.error
                ))

    st.session_state[SESSION_INIT_INFO_PROVIDED] = True
    st.session_state[SESSION_SAVED_USER_INPUT] = None


collected_fact_list_str = get_numerated_list_string(dialog_storage.get_collected_fact_list())
collected_facts_container.markdown(collected_fact_list_str)

# extract answers from facts
if collected_fact_list_str:
    question_list = dialog_navigator.get_question_list_as_numerated()
    extract_answers_from_fact_list(question_list, collected_fact_list_str)

token_count_container.markdown(f'Tokens used: {st.session_state[SESSION_TOKEN_COUNT]}')
question_container.markdown(get_current_question().displayed_message)
collected_dialog_container.dataframe(dialog_storage.get_dialog_list_as_dataFrame(), use_container_width=True, hide_index=True)
explanations_container.dataframe(dialog_navigator.get_question_list_as_dataFrame(), use_container_width=True, hide_index=True)
navigation_data_container.dataframe(dialog_navigator.get_tree_as_dataFrame(), use_container_width=True, hide_index=True)
variable_values = dialog_navigator.get_variable_values()
variable_list_container.markdown(variable_values)
recommendation_container.dataframe(recommendation_manager.get_recommendation_list_as_dataFrame(variable_values), use_container_width=True, hide_index=True)
recommendation_data_container.dataframe(recommendation_manager.get_full_recomendation_list_as_dataFrame(), use_container_width=True, hide_index=True)

