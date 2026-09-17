# -*- coding: utf-8 -*-
"""Exporta content.py a un JSON listo para incrustar en la versión interactiva
(sin speaking) de la Prueba de Nivel de Inglés."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import content as C

LETTERS = "ABCD"

# Plantillas en texto plano para el Open Cloze, con {n} como marcador de hueco.
CLOZE_TEMPLATES = [
    ("B1–B2",
     "Last summer, my sister and I decided to travel around Portugal for two weeks. "
     "We had never been {1} the country before, so we were really excited. On {2} "
     "first day, we visited Lisbon and walked {3} the old streets for hours. The "
     "weather was so hot {4} we had to stop every few minutes to drink water. {5} "
     "of the restaurants we tried were absolutely delicious, especially the fish "
     "dishes. By the end of the trip, we {6} visited five different cities. We "
     "only had ten days, so we {7} to skip the south of the country. We're "
     "already planning {8} go back next year."),
    ("C1–C2",
     "Remote work has transformed the way many of us live and work. {1} has this "
     "shift been more visible than in large cities, where office towers now "
     "stand half-empty. Some economists argue that, {2} the initial disruption, "
     "remote work has ultimately made the workforce more productive. Others, "
     "{3}, believe that it has eroded the sense of community that traditionally "
     "existed within companies. {4} matter which side of the debate you fall "
     "on, it is clear that the traditional nine-to-five office model is unlikely "
     "to return in {5} original form. Employees have grown accustomed to the "
     "flexibility remote work provides, and few would be willing to give it {6} "
     "without a fight. {7} this trend continues, cities may need to rethink {8} "
     "they use office space altogether."),
]

KWT_VARIANTS = [
    ["don't have to finish", "do not have to finish"],
    ["haven't seen her for", "have not seen her for", "haven't seen her in", "have not seen her in"],
    ["was stolen while"],
    ["has been learning english for"],
    ["can't have known", "cannot have known", "can not have known"],
    ["might have missed"],
    ["tired though she was", "though she was tired"],
    ["wish i had studied", "wish i'd studied"],
]


def mcq_list(items):
    return [{"q": q, "opts": opts, "correct": ans} for (q, opts, ans) in items]


def part1_list():
    return [{"q": q, "opts": opts, "correct": ans, "level": lvl} for (lvl, q, opts, ans) in C.PART1]


data = {
    "part1": part1_list(),
    "part2": [
        {
            "level": lvl,
            "template": tmpl,
            "gaps": [{"n": n, "accepted": [a.lower() for a in accepted]}
                     for n, accepted in gaps],
        }
        for (lvl, tmpl), (_orig) in zip(CLOZE_TEMPLATES, C.PART2_TEXTS)
        for gaps in [_orig["gaps"]]
    ],
    "part3": [{"sentence": s, "root": r, "answer": a.lower()} for (s, r, a) in C.PART3],
    "part4": [
        {"orig": orig, "key": key, "prefix": prefix, "suffix": suffix,
         "variants": [v.lower() for v in variants]}
        for (orig, key, prefix, suffix, _ans), variants in zip(C.PART4, KWT_VARIANTS)
    ],
    "part5": mcq_list(C.PART5),
    "scoring": {
        "bands": C.SCORING["bands"],
        "part1_points": C.SCORING["part1_points"],
        "part2_points": C.SCORING["part2_points"],
        "part3_points": C.SCORING["part3_points"],
        "part4_points": C.SCORING["part4_points"],
        "part5_points": C.SCORING["part5_points"],
        "total_points": C.SCORING["total_points"],
    },
}

out_path = Path(__file__).parent / "interactive_data.json"
out_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
print("Escrito:", out_path, out_path.stat().st_size, "bytes")
print("part1:", len(data["part1"]), "part2 gaps:", sum(len(t["gaps"]) for t in data["part2"]),
      "part3:", len(data["part3"]), "part4:", len(data["part4"]), "part5:", len(data["part5"]))
