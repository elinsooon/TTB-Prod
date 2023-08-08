import copy
import numpy as np
from classes import *
from html_fetch import fetch
from itertools import product
import glob
import os
import pandas as pd
import json
import time
from collections import Counter


def gen_course(course_code: str, session: str):
    data = json.loads(fetch(course_code, session))
    if data["payload"] is None:
        return course_code

    course_data = data["payload"]["pageableCourse"]["courses"][0]

    return_course = Course(course_code)

    temp_section_list = []

    for section in course_data["sections"]:
        if check_enrol_control(section):
            section_class = Section(course_code, section["name"], section["linkedMeetingSections"])
            for meeting in section["meetingTimes"]:
                day = meeting["start"]["day"]
                start = meeting["start"]["millisofday"]//1000//60//60
                end = meeting["end"]["millisofday"]//1000//60//60
                section_class.fill_cal(day, start, end)
            if section["type"] == "Lecture":
                for lec in return_course.lectures:
                    if np.array_equal(lec.times, section_class.times):
                        lec.similar_sections.append(section_class)
                        temp_section_list.append(section_class)
                        continue
                if section_class not in temp_section_list:
                    return_course.lectures.append(section_class)
            elif section["type"] == "Tutorial":
                for tut in return_course.tutorials:
                    if np.array_equal(tut.times, section_class.times):
                        tut.similar_sections.append(section_class)
                        temp_section_list.append(section_class)
                        continue
                if section_class not in temp_section_list:
                    return_course.tutorials.append(section_class)
            elif section["type"] == "Practical":
                for pra in return_course.practicals:
                    if np.array_equal(pra.times, section_class.times):
                        pra.similar_sections.append(section_class)
                        temp_section_list.append(section_class)
                        continue
                if section_class not in temp_section_list:
                    return_course.practicals.append(section_class)

    return return_course


def gen_schedules(section_combos: list[list[Section]], filters: FiltersPackage):
    return_list = []
    conflict_list = []
    for sc in section_combos:
        if check_valid_schedule(sc, filters.dow_selected, filters.dow_hard_enforce):
            return_list.append(gen_schedule(sc, filters))
        else:
            conflict_list.extend(find_conflicts(sc))
    return return_list, conflict_list


def gen_schedule(section_combo, filters: FiltersPackage):
    return_sched = np.zeros((5, 12))
    counter = 1

    for section in section_combo:
        test = section.times * counter
        return_sched = return_sched + test
        counter += 1

    return Schedule(return_sched.transpose(), section_combo, filters)


def find_conflicts(sc: list[Section]):
    base = np.zeros((5, 12))

    return_list = []
    for sec in sc:
        base = base + sec.times
        if not (base <= 1).all():
            return_list.append(sec.course_code)
            base[base != 0] = 1
    return return_list


def check_enrol_control(section):
    for i in section["enrolmentControls"]:
        if i["primaryOrg"]["code"] == "ARTSC" or i["primaryOrg"]["code"] == "*":
            return True
    return False


def check_valid_schedule(sections, dow_selected: list[int], dow_hard_enforce: bool):
    result = None
    if not sections:
        return False
    for section in sections:
        ar = np.array(section.times)
        if result is None:
            result = ar
        else:
            result = result+ar
            if dow_hard_enforce:
                for day in dow_selected:
                    if not (result[day] == 0).all():
                        return False
            if not (result <= 1).all():
                return False

        if section.linked_sections:
            for link in section.linked_sections:
                if not any(x.course_code+x.section_code == section.course_code+link for x in sections):
                    return False

    return True


def create_files(schedules, semester):
    to_del = glob.glob(f"{semester}_*.csv") + glob.glob(f"{semester}_*.xlsx")
    for f in to_del:
        os.remove(f)

    for i in range(min(5, len(schedules))):

        np.savetxt(f"{semester}_schedule_{i}.csv", schedules[i].schedule, delimiter=",", fmt="%s")
    all_files = glob.glob(f"{semester}_*.csv")

    writer = pd.ExcelWriter(f"{semester}_schedules.xlsx", engine="xlsxwriter")

    for f in all_files:
        df = pd.read_csv(f)
        df.to_excel(writer, sheet_name=os.path.basename(f), header=False, index=False)
        writer.sheets[os.path.basename(f)].set_column(0, 7, 30)

    writer.save()


def string_code(sec):
    return " " + sec.section_code if not sec.similar_sections else " " + sec.section_code[:3]


def run_program(fall_cl: list[str], winter_cl: list[str], filters: FiltersPackage):
    t = time.time()
    fall_schedules = program_meat(fall_cl, "f", filters)
    if not isinstance(fall_schedules, list):
        return fall_schedules
    else:
        fall_schedules.sort(key=lambda x: x.score, reverse=True)
    winter_schedules = program_meat(winter_cl, "s", filters)
    if not isinstance(winter_schedules, list):
        return winter_schedules
    else:
        winter_schedules.sort(key=lambda x: x.score, reverse=True)
    # year_schedules = program_meat(year_cl, "fs", filters)
    # if not isinstance(year_schedules, list):
    #     return year_schedules
    # else:
    #     year_schedules.sort(key= lambda x: x.score, reverse=True)

    fall_scores = dict(Counter(x.score for x in fall_schedules))
    winter_scores = dict(Counter(x.score for x in winter_schedules))

    print(fall_scores)
    print(winter_scores)

    # fall_temp = []
    # if fall_schedules:
    #     fall_best_score = list(fall_scores.keys())[0]
    #     fall_temp = [sch for sch in fall_schedules if sch.score == fall_best_score]
    # fall_bests = fall_temp
    #
    # winter_temp = []
    # if winter_schedules:
    #     winter_best_score = list(winter_scores.keys())[0]
    #     winter_temp = [sch for sch in winter_schedules if sch.score == winter_best_score]
    # winter_bests = winter_temp

    # make all fall/year combos, sort by score, try all winter combos sorted by score

    # if year_schedules:
    #     return_schedules = []
    #     for year_sched in year_schedules:
    #         year_list = []
    #         for fall_sched in fall_schedules:
    #             if not (year_sched.schedule*fall_sched.schedule == 0).all():
    #                 continue
    #             else:
    #                 fall_year_schedule = combine_schedules(fall_sched, year_sched, filters)
    #                 year_list.append(fall_year_schedule)
    #         year_list.sort(key=lambda x: x.score, reverse=True)
    #         for winter_sched in winter_schedules:
    #             if not (year_sched.schedule*winter_sched.schedule == 0).all():
    #                 continue
    #             else:
    #                 return_schedules.append()
    #
    #                 for winter_sched in winter_bests:
    #                     result2 = year_sched.schedule*winter_sched.schedule
    #                     if not (result2 == 0).all():
    #                         continue
    #                     else:
    #                         return_schedules.append((fall_year_schedule, combine_schedules(year_sched, winter_sched, filters)))
    #
    #         for i in return_schedules:
    #             for j in i:
    #                 counter = 1
    #                 j.schedule = j.schedule.astype("object")
    #
    #                 for section in j.section_combo:
    #                     j.schedule[j.schedule == counter] = section.course_code + string_code(section)
    #                     counter += 1
    #                 j.schedule[j.schedule == 0] = ""
    #
    #     return return_schedules
    #
    # print("post-year")

    for i in fall_schedules:
        counter = 1
        i.schedule = i.schedule.astype("object")
        for section in i.section_combo:
            i.schedule[i.schedule == counter] = section.course_code + string_code(section)
            counter += 1
        i.schedule[i.schedule == 0] = ""

    for i in winter_schedules:
        counter = 1
        i.schedule = i.schedule.astype("object")

        for section in i.section_combo:
            i.schedule[i.schedule == counter] = section.course_code + string_code(section)
            counter += 1
        i.schedule[i.schedule == 0] = ""

    print(f"time elapsed: {time.time() - t}")
    return [fall_schedules, winter_schedules]


def combine_schedules(sched1, sched2, filters):
    new_sched_array = sched1.schedule.copy()
    new_sched_sections = sched1.section_combo[:]
    counter = np.max(sched1.schedule) + 1
    for section in sched2.section_combo:
        new_sched_array = new_sched_array + section.times.transpose()*counter
        new_sched_sections.append(section)
        counter += 1

    return Schedule(new_sched_array, new_sched_sections, filters)


def program_meat(course_list: list[str], session: str, filters: FiltersPackage):
    courses: list[Course] = []
    sections = []

    for course in course_list:
        gen = gen_course(course, session)
        if not isinstance(gen, Course):
            return CustomException("Existence", gen)
        courses.append(gen)
        if gen.lectures:
            sections.append(gen.lectures)
        if gen.tutorials:
            sections.append(gen.tutorials)
        if gen.practicals:
            sections.append(gen.practicals)

    courses.sort(key=lambda x: (len(x.lectures)+len(x.tutorials)))

    section_combos = [list(t) for t in list(product(*sections))]
    print("check in: "+str(len(section_combos)))
    schedules = gen_schedules(section_combos, filters)

    if schedules[0] != []:
        schedules[0].sort(key=lambda x: x.score, reverse=True)
        return schedules[0]
    elif schedules[1] == []:
        return schedules[0]
    else:
        temp = Counter(schedules[1])
        return CustomException("Conflict", max(temp, key=temp.get))


def select_schedules(schedules, fall_best_score, winter_best_score):
    fall_selected = []
    winter_selected = []

    if fall_best_score is not None:
        fall_bests = [sch for sch in schedules[0] if sch.score == fall_best_score]
        current_fall = None
        for sched in fall_bests:
            if current_fall is None:
                fall_selected.append(sched)
                current_fall = sched
                continue
            if np.sum(current_fall.schedule != sched.schedule) >= 4:
                fall_selected.append(sched)
                current_fall = sched

    if winter_best_score is not None:
        winter_bests = [sch for sch in schedules[1] if sch.score == winter_best_score]
        current_winter = None
        for sched in winter_bests:
            if current_winter is None:
                winter_selected.append(sched)
                current_winter = sched
                continue
            if np.sum(current_winter.schedule != sched.schedule) >= 4:
                winter_selected.append(sched)
                current_winter = sched

    return [fall_selected, winter_selected]
