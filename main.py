import datetime
from utility import run_program, create_files, select_schedules
from classes import TimetableStyler, FiltersPackage, CustomException
import re
import pandas as pd
import streamlit as st
from collections import Counter
import numpy as np


# CSC236,STA302,STA304,MAT224,CRE275
# CSC258,CSC263,MAT244,STA303,PHL281
# fall_cl = ["PSL304", "PSL372", "HMB302", "MHB155", "NFS284"]
# fall_cl = ["CSC236", "STA302", "STA304", "MAT224", "CRE275"]
# winter_cl = ["CSC258", "CSC263", "MAT244", "STA303", "PHL281"]

st.set_page_config(layout="wide")

st.title("TTB")
st.header("It's better.")
st.write("Input your courses for each semester seperated by commas")
st.write("e.g. CSC236, CSC258, STA302, STA304, PHL281")

fall_cl = []
winter_cl = []

schedules = None

colors = [
            "EA80FC",
            "FF80AB",
            "8C9EFF",
            "A7FFEB",
            "F4FF81",
            "FFD180"
        ]

dow_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
dow_dict = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}


with st.form("course_lists"):
    text_fall_cl = st.text_input("enter your fall courses",
                                 "")
    text_winter_cl = st.text_input("enter your winter courses",
                                   "")
    # text_year_cl = st.text_input("enter your year-long courses",
    #                              "mat137")

    form_col1, form_col2, form_col3, form_col4, form_col5, form_col6 = st.columns(6)

    before_time = form_col1.time_input(label="No courses before ___ o'clock (when possible)", step=3600, value=datetime.time(10, 0))
    before_importance = form_col2.selectbox(
        "How important is this? (0: least, 5: most)",
        options=list(i for i in range(1, 6)),
        key="before",
        index=0
    )

    after_time = form_col1.time_input(label="No courses after ___ o'clock (when possible)", step=3600, value=datetime.time(17, 0))
    after_importance = form_col2.selectbox(
        "How important is this? (0: least, 5: most)",
        options=list(i for i in range(1, 6)),
        key="after",
        index=0
    )

    dow_selection = form_col4.multiselect(
        "No courses on ____'s",
        options=dow_list
    )
    form_col5.markdown("#")
    dow_selection_hard = form_col5.checkbox("It's a requirement, not a preference")

    max_daily_courses = form_col1.selectbox(
        "Maximum hours of courses per day",
        options=list(i for i in range(13)),
        key="max",
        index=4
    )
    max_daily_courses_importance = form_col2.selectbox(
        "How important is this? (0: least, 5: most)",
        options=list(i for i in range(1, 6)),
        key="max_imp",
        index=0
    )

    submitted = st.form_submit_button(label="Submit")
    if submitted:
        loading = st.empty()
        loading.write("Loading...")
        fall_temp = [i.upper() for i in re.split(',|, | ', text_fall_cl.replace(" ", ""))]
        winter_temp = [i.upper() for i in re.split(',|, | ', text_winter_cl.replace(" ", ""))]
        # year_temp = [i.upper() for i in re.split(',|, | ', text_year_cl.replace(" ", ""))]
        fall_cl = fall_temp if fall_temp != [''] else []
        winter_cl = winter_temp if winter_temp != [''] else []
        # year_cl = year_temp if year_temp != [''] else []
        schedules = run_program(fall_cl, winter_cl, FiltersPackage(before_time,
                                                                   int(before_importance),
                                                                   after_time, int(after_importance),
                                                                   [dow_dict.get(dow) for dow in dow_selection],
                                                                   dow_selection_hard,
                                                                   max_daily_courses,
                                                                   max_daily_courses_importance))
        # create_files(schedules[0], "fall")
        # create_files(schedules[1], "winter")

        # year_colors = {year_cl[i]: colors[len(colors) - i - 1] for i in range(len(year_cl))}
        fall_colors = {fall_cl[i]: colors[i] for i in range(len(fall_cl))}  # | year_colors
        winter_colors = {winter_cl[i]: colors[i] for i in range(len(winter_cl))}  # | year_colors

if isinstance(schedules, CustomException):

    # if a course code is invalid, run_program returns a string
    # of that course code, rather than schedule data

    if schedules.exc_type == "Existence":
        st.write(f"{schedules.body} is not a valid input, please choose a real course or fix formatting")
    elif schedules.exc_type == "Conflict":
        st.write(f"{schedules.body} is posing many conflicts which may be preventing any schedules from being generated, please try removing it or swapping it for another course")
    else:
        st.write("Wow you really broke it")

    loading.empty()

elif schedules:
    loading.empty()
    if all(isinstance(i, list) for i in schedules):
        fall_scores = dict(Counter(x.score for x in schedules[0]))
        winter_score = dict(Counter(x.score for x in schedules[1]))

        print(fall_scores)
        print(winter_score)

        fall_best_score = None
        if schedules[0]:
            fall_best_score = list(fall_scores.keys())[0]

        winter_best_score = None
        if schedules[1]:
            winter_best_score = list(winter_score.keys())[0]

        selected_schedules = select_schedules(schedules, fall_best_score, winter_best_score)

        col1, col2 = st.columns(2)

        for i in range(min(5, len(selected_schedules[0]))):
            tts1 = TimetableStyler(fall_colors)
            df1 = pd.DataFrame(selected_schedules[0][i].schedule,
                               columns=dow_list,
                               index=list('%d :00' % i for i in range(9, 21)))
            df1 = df1.style.applymap(tts1.get_course_color)
            df1 = df1.set_properties(**{"text-align": "center"})
            col1.dataframe(df1, height=455, use_container_width=True)

        for i in range(min(5, len(selected_schedules[1]))):
            tts2 = TimetableStyler(winter_colors)
            df2 = pd.DataFrame(selected_schedules[1][i].schedule,
                               columns=dow_list,
                               index=list('%d :00' % i for i in range(9, 21)))
            df2 = df2.style.applymap(tts2.get_course_color)
            df2 = df2.set_properties(**{"text-align": "center"})
            col2.dataframe(df2, height=455, use_container_width=True)

    # elif all(isinstance(i, tuple) for i in schedules):
    #     scores = dict(Counter(x.score+y.score for (x, y) in schedules))
    #     print(scores)
    #     best_score = list(scores.keys())[0]
    #
    #     bests = [sch for sch in schedules if sch[0].score+sch[1].score == best_score]
    #
    #     selected = []
    #     current = None
    #     for sched in bests:
    #         if current is None:
    #             selected.append(sched)
    #             current = sched
    #             continue
    #         if np.sum(current[0].schedule != sched[0].schedule) >= 4 or np.sum(current[1].schedule != sched[1].schedule) >= 4:
    #             selected.append(sched)
    #             current = sched
    #     col1, col2 = st.columns(2)
    #
    #     for i in range(min(5, len(selected))):
    #         tts1 = TimetableStyler(fall_colors)
    #         df1 = pd.DataFrame(selected[i][0].schedule)
    #         df1 = df1.style.applymap(tts1.get_course_color)
    #         col1.table(df1)
    #         tts2 = TimetableStyler(winter_colors)
    #         df2 = pd.DataFrame(selected[i][1].schedule)
    #         df2 = df2.style.applymap(tts2.get_course_color)
    #         col2.table(df2)

if schedules == []: # don't try simplifying this, if you make it "if not schedules" it displays the text on page load
    loading.empty()
    st.write("No possible schedules with these criteria :(")
    st.write("Try making your selections less restrictive")
print("done")
