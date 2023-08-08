import datetime
import numpy as np


class FiltersPackage:
    def __init__(self, before: datetime.time, b_imp: int,
                 after: datetime.time, a_imp: int,
                 dow_selected: list[int], dow_hard_enforce: bool,
                 max_daily: int, max_daily_imp: int):
        self.before = before
        self.b_imp = b_imp
        self.after = after
        self.a_imp = a_imp
        self.dow_selected = dow_selected
        self.dow_hard_enforce = dow_hard_enforce
        self.max_daily = max_daily
        self.max_daily_imp = max_daily_imp


class Section:
    course_code: str
    section_code: str
    times: np.array
    linked_sections: list
    similar_sections: list

    def __init__(self, course_code, section_code, linked_sec):
        self.course_code = course_code
        self.section_code = section_code
        self.times = np.zeros((5, 12))
        self.linked_sections = []
        self.similar_sections = []

        if linked_sec:
            for section in linked_sec:
                self.linked_sections.append(section["teachMethod"] + section["sectionNumber"])

    def fill_cal(self, day, start, end):
        for i in range(start-9, end-9):
            self.times[day-1, i] = 1


class Course:
    course_code: str
    lectures: list[Section]
    tutorials: list[Section]
    practicals: list[Section]

    def __init__(self, course_code):
        self.course_code = course_code
        self.lectures = []
        self.tutorials = []
        self.practicals = []


class Schedule:
    schedule: np.array
    score: int
    section_combo: list
    filters: FiltersPackage

    def __init__(self, schedule, section_combo, filters):
        self.schedule = schedule
        self.filters = filters
        self.score = self.gen_score()
        self.section_combo = section_combo

    def gen_score(self):
        score = 0
        for day in range(5):
            num_courses = 0
            for hour in range(12):
                if self.schedule[hour, day] != 0:
                    if day in self.filters.dow_selected and not self.filters.dow_hard_enforce:
                        score -= 1
                    num_courses += 1
                    if hour <= self.filters.before.hour - 9:
                        score -= self.filters.b_imp
                    if hour >= self.filters.after.hour - 9:
                        score -= self.filters.a_imp
                    if num_courses > self.filters.max_daily:
                        score -= self.filters.max_daily_imp

        return score


class TimetableStyler:
    def __init__(self, colors: dict[str, str]) -> None:
        self.colors = colors

    def get_course_color(self, section: str):
        if section:
            course = section.split()[0]
            return f'background-color: #{self.colors[course]}'
        else:
            return 'background-color: #ffffff'


class CustomException:
    def __init__(self, exc_type: str, body):
        self.exc_type = exc_type
        self.body = body
