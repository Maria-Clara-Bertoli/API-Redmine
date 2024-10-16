import time
import os
import numpy as np
import streamlit as st
from model import util

include_sprint, visualize_sprint = st.tabs(["Incluir Sprint", "Visualizar Sprints"])

with include_sprint:

    subheader = st.subheader("Inclua Sprints Aqui! 👇")
    task_id_list = []

    with st.form(key="form", clear_on_submit=True):

        sprint_name = st.text_input(label="Nome da Sprint")
        sprint_start_date = st.date_input(label="Data Inicial da Sprint")
        sprint_end_date = st.date_input(label="Data Final da Sprint")
        task_id_text = st.text_area(label="IDs das Tarefa", help="Insira Todos os IDs das Tarefas que Devem Compor uma Sprint no Seguinte Formato: '[...]100, 101, 102[...]'")
        submit = st.form_submit_button(label="Adicionar Tarefas", use_container_width=True)

        if submit:
            text_validation = util.text_validation(task_id_text)
            date_validation = util.date_validation(sprint_start_date, sprint_end_date)

            if text_validation and date_validation:
                task_id_list = util.text_formatting(task_id_text)
                message = st.success("Envio de Tarefas Realizado!", icon="✅")
                time.sleep(3)
                message.empty()
            else:
                task_id_list = []
                message = st.error("Um Erro Ocorreu ao Enviar as Tarefas. Verifique a Sintaxe Fornecida e Atente-se as Datas de Início e Fim da Sprint!", icon="🔥")
                time.sleep(3)
                message.empty()
        
    if task_id_list:
        sprint_validation = util.create_sprint(sprint_name, sprint_start_date, sprint_end_date, task_id_list)
        if not sprint_validation:
            message = st.warning("A Sprint Não Foi Criada. Há incompatibilidade de Datas Entre a Sprint e as Tarefas!", icon="😔")
            time.sleep(3)
            message.empty()
        
with visualize_sprint:

    element = 0
    rows = []
    containers = []
    sprints = []
    sprint_files = os.listdir("sprint")

    if not sprint_files:
        st.warning("Não Há Sprints para Visualizar no Momento!", icon="🧐")
        st.stop()
    else:
        if "sprint_state" not in st.session_state:
            st.session_state.sprint_state = util.read_sprint(f"sprint/{sprint_files[0]}")

    len_sprint_dir = len(sprint_files)
    half_len_sprint_dir = int(np.ceil(len_sprint_dir/2))

    for index in range(0, half_len_sprint_dir):
        rows.append(st.columns(2))
    
    for index in range(0, len_sprint_dir):
        sprint = util.read_sprint(f"sprint/{sprint_files[index]}")
        sprints.append(sprint)

    for row in rows:
        for column in row:
            with column.container(height=180):
                if element + 1 <= len_sprint_dir:
                    subheader = st.subheader(f"{sprints[element].attrs["start_date"]} : {sprints[element].attrs["end_date"]}")
                    write = st.write(f"{sprints[element].attrs["name"]}")

                    if st.button(label="Detalhar Sprint", key=element, disabled=False, use_container_width=True):
                        st.session_state.sprint_state = sprints[element]
                        st.switch_page("view/chart.py")
                else:
                    subheader = st.subheader(f"----- : -----")
                    write = st.write(f"Esperando Próxima Sprint...")
                    button = st.button(label="Detalhar Sprint", key=element, disabled=True, use_container_width=True)
                element = element + 1