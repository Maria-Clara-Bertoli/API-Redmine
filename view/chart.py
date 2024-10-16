import os
from model import util
import streamlit as st
import pandas as pd
from datetime import datetime

show_sprint, show_burndown = st.tabs(["Mostrar Sprint", "Mostrar Burndown"])

with show_sprint:

    sprint_files = os.listdir("sprint")

    if not sprint_files:
        st.warning("Não Há Sprints para Visualizar no Momento!", icon="🧐")
        st.stop()
    else:
        if "sprint_state" not in st.session_state:
            st.session_state.sprint_state = util.read_sprint(f"sprint/{sprint_files[0]}")

    st.dataframe(data=st.session_state.sprint_state, height=500, use_container_width=True, hide_index=True)

with show_burndown:
    
    working_days = util.difference_between_date(st.session_state.sprint_state.attrs["start_date"], st.session_state.sprint_state.attrs["end_date"])
    list_days, linear_list_tasks = util.linear_distribute_tasks(st.session_state.sprint_state, working_days)
    _, not_linear_list_tasks = util.not_linear_distribute_tasks(st.session_state.sprint_state, working_days, st.session_state.sprint_state.attrs["start_date"])
    
    chart_data = pd.DataFrame({"list_days":list_days, "linear_list_tasks":linear_list_tasks, "not_linear_list_tasks":not_linear_list_tasks})
    burndown_chart = st.line_chart(chart_data, x="list_days", y=["linear_list_tasks", "not_linear_list_tasks"], x_label="DIAS", y_label="TAREFAS", color=["#FF0000", "#0000FF"], height=500, use_container_width=True)
