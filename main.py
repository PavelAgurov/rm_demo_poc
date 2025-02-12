"""
    Main APP and UI
"""
# pylint: disable=C0301,C0103,C0303,R0913,R0914,C0412

from datetime import datetime
import json
import os
import pandas as pd

import streamlit as st

import langchain
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain_community.cache import SQLiteCache
from langchain_core.runnables.base import RunnableSequence

from dialog_storage import DialogStorage, DialogItem
from prompts import extract_facts_prompt_template, score_all_prompt_template, value_item_prompt_template, score_one_prompt_template
from utils import get_numerated_list_string, get_fixed_json
from navigation import TreeNodeAnswer, TreeDialogNavigator, BaseNavigationQuestion
from navigation_tree_json import tree_json
from session_manager import StreamlitSessionManager
from strings import HOW_IT_WORKS, APP_HEADER, INITIAL_INFO_MESSAGE, ADDITIONAL_INFO_MESSAGE
from classes import CurrentQuestion, ExtratedFactList
from utils_streamlit import streamlit_hack_remove_top_space
from emulator import EMULATOR_get_fact_list, EMULATOR_set_answers, EMULATOR_set_value_items, LLM_EMULATOR_INFO_HTML
from recommendation import RecommendationManager
from recommendation_json import recommendation_json
from values import ValueItemAnswer, ValueItemManager
from values_json import values_items_json
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
    input_str : str = st.session_state.user_input
    input_str = input_str.strip()
    st.session_state[SESSION_SAVED_USER_INPUT] = input_str
    st.session_state.user_input = ""

# ------------------------------- UI
st.set_page_config(page_title= APP_HEADER, layout="wide")
st.title(APP_HEADER)

error_data_container     = st.empty()
recommendation_container = st.container().empty()

streamlit_hack_remove_top_space()

tab_main, tab_setting, tab_data, tab_debug = st.tabs(["Request", "Settings", "Data", "Debug"])
with tab_main:
    header_container     = st.container()
    if LLM_EMULATOR:
        emulator_container = st.empty()
    question_container     = st.empty()
    input_container        = st.container()
    input_container.text_area("Your answer or request: ", "", key="user_input", on_change= submit_user_input)  
    status_container       = st.empty()
    explanations_container = st.expander(label="Explanations").empty()
    value_item_container   = st.expander(label="Value items").empty()
    variable_list_container = st.expander(label="Calculated variables").empty()
    debug_container        = st.container()

with tab_setting:
    open_api_key = st.text_input("OpenAPI Key: ", "", key="open_api_key")
    st.info("""\
            System can check all question in one request or check it one by one. Second option is more expensive (used more tokens),
            but it has better quality.
    """)
    cb_process_all_question = st.checkbox(label="Process all questions at once", value=False)
    st.info("""\
            Direct answer means that user provide answer the question (yes/no or text). System will analizy all additionally
            provided information, but use direct answer without LLM checking.
    """)
    cb_use_direct_answer_in_tree = st.checkbox(
        label="Do not calculate dialog node by LLM if there is direct answer",
        disabled = cb_process_all_question,
        value=True
    )
    st.info("""\
            System can permanently save answer and do not re-calculate it with new facts. In this case system can't 
            indentify contradictive answers, but it will improve performance.
    """)
    do_not_calculate_answered = st.checkbox(label="Do not re-calculate already answered questions", value=True)

with tab_data:
    navigation_data_container = st.expander(label="Navigation data").empty()
    navigation_tree_container_expander = st.expander(label="Navigation tree")
    navigation_tree_container_link = navigation_tree_container_expander.empty()
    navigation_tree_container = navigation_tree_container_expander.empty()
    value_items_data_container = st.expander(label="Value items data").empty()
    recommendation_data_container = st.expander(label="Recommendations").empty()

with tab_debug:
    facts_from_dialog_conteiner = st.expander(label="Fact JSON").empty()
    score_result_container = st.expander(label="Score JSON").empty()
    value_item_result_container = st.expander(label="Value items JSON").empty()

with st.sidebar:
    collected_dialog_container = st.expander(label="Saved dialog").empty()
    token_count_container      = st.empty()
    collected_facts_container  = st.expander(label="Facts", expanded=True).empty()
    collected_direct_answers_container  = st.expander(label="Direct answers", expanded=True).empty()

header_container.markdown(HOW_IT_WORKS, unsafe_allow_html=True)

#------------------------------- Functions

def get_current_question(html_view : bool) -> CurrentQuestion:
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
        if not html_view:
            message = f'[{dialog_node_id}] {question.question}\n{question.context}'
        else:
            message = f'[{dialog_node_id}] {question.question}<br/>{question.context}'
        return CurrentQuestion(dialog_node_id, question.question, message)

    # end of dialog
    return CurrentQuestion(None, None, ADDITIONAL_INFO_MESSAGE)

def get_fact_list_from_question_answer(node_id : int, question : str, provied_answer : str) -> ExtratedFactList:
    """
        Get facts extracted from question and answer
    """
    if LLM_EMULATOR:
        return EMULATOR_get_fact_list(node_id, provied_answer)

    # use real LLM
    facts_from_dialog = None
    status_container.markdown('Starting LLM to extract facts...')
    with get_openai_callback() as cb:
        facts_from_dialog = extract_facts_chain.invoke({"question" : question, "answer" : provied_answer})
    st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
    status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
    facts_from_dialog_conteiner.markdown(facts_from_dialog)

    error = False
    fact_list_from_a2q = []
    direct_answer = None
    try:
        facts_from_dialog_json = json.loads(get_fixed_json(facts_from_dialog))
        facts_it_json = facts_from_dialog_json['it_project_facts']
        fact_list_from_a2q = [f['fact'] for f in facts_it_json]
        if node_id and question: # direct answer can be only if we have node and question
            if 'direct_answer' in facts_from_dialog_json:
                direct_answer = facts_from_dialog_json['direct_answer']
    except:  # noqa: E722 # pylint: disable=W0702
        error = True
    return ExtratedFactList(fact_list_from_a2q, direct_answer, error)

def answer2bool(answer_str : str) -> bool:
    """Convert answer string into bool or None"""
    answer_str = answer_str.lower()
    if answer_str in ["yes", "y", "true"]:
        return 1
    if answer_str in ["no", "n", "false"]:
        return 0
    return None


def extract_answers_from_fact_list(
        navigator : TreeDialogNavigator,
        chain : RunnableSequence,
        question_list_str : str,
        fact_list_str : str
    ):
    """Extract answers from fact list"""

    if LLM_EMULATOR:
        EMULATOR_set_answers(fact_list_str, navigator)
        return

    status_container.markdown('Starting LLM to extract answers...')
    with get_openai_callback() as cb:
        score_result = chain.invoke({"questions" : question_list_str, "facts" : fact_list_str})
    st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
    status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
    score_result_container.markdown(score_result)

    try:
        score_result_json = json.loads(get_fixed_json(score_result))
        for answer_json in score_result_json:
            question_id  = int(answer_json["QuestionID"])
            answer_value = answer2bool(answer_json["Answer"])
            answer = TreeNodeAnswer(answer_json["Score"], answer_value, answer_json["Explanation"], answer_json["RefFacts"])
            navigator.set_node_answer(question_id, answer)
    except Exception as error: # pylint: disable=W0718,W0702
        debug_container.markdown(f'Error parsing answer. JSON:\n{score_result}\n\n{error}')

def extract_answers_from_fact_list_one(
        navigator : TreeDialogNavigator,
        chain : RunnableSequence,
        question_list : list[BaseNavigationQuestion],
        fact_list_str : str,
        use_direct_answer_in_tree : bool,
        direct_answers : dict[int, str],
        skip_answered : bool
    ):
    """Extract answers from fact list one by one"""

    score_result_list = []
    for question in question_list:

        if skip_answered and question.node_id: # skip calculation if we have answer already
            node_answer = navigator.get_node_answer(question.node_id)
            if (node_answer is not None) and (node_answer.answer_bool is not None):
                print(f'{question.node_id} has answer already - skip')
                continue

        if use_direct_answer_in_tree: # we can use direct answers for navigation
            if question.node_id and (question.node_id in direct_answers): # we have direct answer for this question
                node_direct_answer_value = direct_answers[question.node_id]
                node_direct_answer_bool = answer2bool(node_direct_answer_value)
                node_direct_answer_str = f'Direct answer for node {question.node_id}: {node_direct_answer_value} [{node_direct_answer_bool}]'
                node_direct_answer = TreeNodeAnswer(1, node_direct_answer_bool, "Direct answer", None)
                navigator.set_node_answer(question.node_id, node_direct_answer)
                print(node_direct_answer_str)
                score_result_list.append(node_direct_answer_str)
                continue

        status_container.markdown(f'Starting LLM to extract answers {question.node_id}/{len(question_list)}...')
        with get_openai_callback() as cb:
            score_result = chain.invoke({"question" : question, "facts" : fact_list_str})
        st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
        status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
        score_result_list.append(score_result)

        try:
            score_result_json = json.loads(get_fixed_json(score_result))
            for answer_json in score_result_json:
                answer_value = answer2bool(answer_json["Answer"])
                answer = TreeNodeAnswer(answer_json["Score"], answer_value, answer_json["Explanation"], answer_json["RefFacts"])
                navigator.set_node_answer(question.node_id, answer)
        except Exception as error: # pylint: disable=W0718,W0702
            debug_container.markdown(f'Error parsing answer. JSON:\n{score_result}\n\n{error}')
    score_result_container.markdown("\n\n".join(score_result_list))


def extract_value_items_from_fact_list(
        manager : ValueItemManager,
        chain : RunnableSequence,
        items_list_str : str,
        fact_list_str : str
    ):
    """Extract value items from fact list"""

    if LLM_EMULATOR:
        EMULATOR_set_value_items(fact_list_str, manager)
        return

    status_container.markdown('Starting LLM to extract value items...')
    with get_openai_callback() as cb:
        score_result = chain.invoke({"questions" : items_list_str, "facts" : fact_list_str})
    st.session_state[SESSION_TOKEN_COUNT] += cb.total_tokens
    status_container.markdown(f'Done. Used {cb.total_tokens} tokens.')
    value_item_result_container.markdown(score_result)

    try:
        score_result_json = json.loads(get_fixed_json(score_result))
        for answer_json in score_result_json:
            question_id  = int(answer_json["QuestionID"])
            answer       = answer_json["Answer"]
            answer = ValueItemAnswer(answer_json["Score"], answer, answer_json["Explanation"], answer_json["RefFacts"])
            manager.set_answer(question_id, answer)
    except Exception as error: # pylint: disable=W0718,W0702
        debug_container.markdown(f'Error parsing answer. JSON:\n{score_result}\n\n{error}')

#------------------------------- LLM setup

if open_api_key:
    LLM_OPENAI_API_KEY = open_api_key
else:
    LLM_OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

langchain.llm_cache = SQLiteCache()

llm = ChatOpenAI(model_name = "gpt-4o-mini", openai_api_key = LLM_OPENAI_API_KEY, max_tokens = 1000, temperature = 0)

extract_facts_prompt = ChatPromptTemplate.from_template(extract_facts_prompt_template)
extract_facts_chain  = extract_facts_prompt | llm | StrOutputParser()
score_all_prompt = ChatPromptTemplate.from_template(score_all_prompt_template)
score_all_chain  = score_all_prompt | llm | StrOutputParser()
score_one_prompt = ChatPromptTemplate.from_template(score_one_prompt_template)
score_one_chain  = score_one_prompt | llm | StrOutputParser()
value_item_prompt = ChatPromptTemplate.from_template(value_item_prompt_template)
value_item_chain  = value_item_prompt | llm | StrOutputParser()

if LLM_EMULATOR:
    emulator_container.markdown(LLM_EMULATOR_INFO_HTML, unsafe_allow_html=True) # pylint: disable=E0601

#------------------------------- Main objects

session_manager  = StreamlitSessionManager()
dialog_storage   = DialogStorage(session_manager)
dialog_navigator = TreeDialogNavigator(tree_json, session_manager)
value_item_manager = ValueItemManager(values_items_json, session_manager)
recommendation_manager = RecommendationManager(recommendation_json, session_manager)

#------------------------------- Minor data validations
data_errors = []
all_variables = dialog_navigator.get_all_variable_names() + value_item_manager.get_all_variable_names()
duplicates = list(set([x for x in all_variables if all_variables.count(x) > 1]))
if len(duplicates) > 0:
    data_errors.append(f'There are duplicates in the data: {duplicates}')
recommendation_errors = recommendation_manager.get_unknown_valiable_list(all_variables)
if len(recommendation_errors) > 0:
    data_errors.append(f'There are unknown variable in recommendations: {recommendation_errors}')
if len(data_errors) > 0:
    error_message = "<br>".join(data_errors)
    error_message = f'<p style="color:white; background-color:red">{error_message}</p>'
    error_data_container.markdown(error_message, unsafe_allow_html=True)
#------------------------------- APP

# show data
navigation_data_container.dataframe(dialog_navigator.get_tree_as_dataFrame(), use_container_width=True, hide_index=True)
value_items_data_container.dataframe(value_item_manager.get_list_as_dataFrame(), use_container_width=True, hide_index=True)
navigation_tree_container.graphviz_chart(dialog_navigator.get_dialog_graph(True), use_container_width  = True)
recommendation_data_container.dataframe(recommendation_manager.get_full_recomendation_list_as_dataFrame(), use_container_width=True, hide_index=True)

current_question : CurrentQuestion = get_current_question(True)
question_container.markdown(current_question.displayed_message, unsafe_allow_html=True)
token_count_container.markdown(f'Tokens used: {st.session_state[SESSION_TOKEN_COUNT]}')

user_input : str = st.session_state[SESSION_SAVED_USER_INPUT]
if user_input:
    extracted_fact_list = get_fact_list_from_question_answer(
                                current_question.dialog_node_id, 
                                current_question.current_question, 
                                user_input)

    # save dialog in the storage
    dialog_storage.add_dialog(DialogItem(
                    datetime.now(),
                    current_question.dialog_node_id,
                    current_question.current_question,
                    user_input,
                    extracted_fact_list.facts,
                    extracted_fact_list.direct_answer,
                    extracted_fact_list.error
                ))

    st.session_state[SESSION_INIT_INFO_PROVIDED] = True
    st.session_state[SESSION_SAVED_USER_INPUT] = None


collected_fact_list_str = get_numerated_list_string(dialog_storage.get_collected_fact_list())
collected_facts_container.markdown(collected_fact_list_str)

collected_direct_answers = dialog_storage.get_collected_direct_answers()
collected_direct_answers_container.markdown('<br/>'.join([f'{a[0]}: {a[1]}' for a in collected_direct_answers.items()]), unsafe_allow_html=True)
collected_dialog_container.dataframe(dialog_storage.get_dialog_list_as_dataFrame(), use_container_width=True, hide_index=True)

# extract answers from collected facts
if collected_fact_list_str:
    if cb_process_all_question:
        numerated_question_list_str = dialog_navigator.get_question_list_as_numerated()
        extract_answers_from_fact_list(dialog_navigator, score_all_chain, numerated_question_list_str, collected_fact_list_str)
    else:
        full_question_list = dialog_navigator.get_question_list()
        extract_answers_from_fact_list_one(
            dialog_navigator,
            score_one_chain,
            full_question_list,
            collected_fact_list_str,
            cb_use_direct_answer_in_tree,
            collected_direct_answers,
            do_not_calculate_answered
        )

    value_items_list_str = value_item_manager.get_list_as_numerated()
    extract_value_items_from_fact_list(value_item_manager, value_item_chain, value_items_list_str, collected_fact_list_str)

token_count_container.markdown(f'Tokens used: {st.session_state[SESSION_TOKEN_COUNT]}')
question_container.markdown(get_current_question(True).displayed_message, unsafe_allow_html=True)
explanations_container.dataframe(dialog_navigator.get_question_list_as_dataFrame(), use_container_width=True, hide_index=True)

value_item_container.dataframe(value_item_manager.get_values_as_dataFrame(), use_container_width=True, hide_index=True)

variable_values_from_dialog : dict[str, bool] = dialog_navigator.get_variable_values()
variable_value_from_value_items : dict[str, bool] = value_item_manager.get_variable_values()
variable_values = variable_values_from_dialog | variable_value_from_value_items
variable_list_container.dataframe(pd.DataFrame([[v[0], v[1]] for v in variable_values.items()], columns=['Name', 'Value']), use_container_width=True, hide_index=True)
recommendation_container.markdown(
    recommendation_manager.get_recommendation_list_as_dataFrame(variable_values).to_html(
        render_links=True, 
        escape=False, 
        index = False
    ), 
    unsafe_allow_html=True
)

# if png was generated - we can download it
if os.path.isfile(dialog_navigator.file_name):
    with open(dialog_navigator.file_name, 'rb') as f:
        navigation_tree_container_link.download_button('Download Png', f, file_name='digraph.png') 
