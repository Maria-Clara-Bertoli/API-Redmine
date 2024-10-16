import streamlit as st

sprint = st.Page(
    page = "view/sprint.py",
    title = "Sprints",
    icon = ":material/table:",
    default = True,
)

chart = st.Page(
    page = "view/chart.py",
    title = "Gráficos",
    icon = ":material/monitoring:",
)

pages = st.navigation({"MENU":[sprint, chart]})
pages.run()