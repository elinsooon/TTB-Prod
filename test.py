import numpy as np
from utility import run_program, gen_course, select_schedules
import re
from collections import Counter

if __name__ == "__main__":
    fall_cl = ["CSC236", "STA302", "STA304", "CRE275"]
    winter_cl = ["CSC258", "CSC263", "STA303", "PHL281"]
    year_cl = [""]

    # text_fall_cl = "CSC236, STA302,STA304, MAT224,CRE275"
    # text_fall_cl = text_fall_cl.replace(" ", "")
    # fall_cl = re.split(',|, | ', text_fall_cl)

    # test = gen_course("CSC101", "f")
    schedules = run_program(fall_cl, winter_cl, year_cl)

    if all(isinstance(i, list) for i in schedules):
        fall_scores = dict(Counter(x.score for x in schedules[0]))
        winter_score = dict(Counter(x.score for x in schedules[1]))

        print(fall_scores)
        print(winter_score)

        fall_best_score = list(fall_scores.keys())[0]
        winter_best_score = list(winter_score.keys())[0]

        selected_schedules = select_schedules(schedules, fall_best_score, winter_best_score)
    elif all(isinstance(i, tuple) for i in schedules):
        scores = dict(Counter(x.score+y.score for (x, y) in schedules))
        print(scores)
        best_score = list(scores.keys())[0]

        bests = [sch for sch in schedules if sch[0].score+sch[1].score == best_score]

        selected = []
        current = None
        for sched in bests:
            if current is None:
                selected.append(sched)
                current = sched
                continue
            if np.sum(current[0].schedule != sched[0].schedule) >= 4 or np.sum(current[1].schedule != sched[1].schedule) >= 4:
                selected.append(sched)
                current = sched

    print("end test")
