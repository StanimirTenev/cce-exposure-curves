#!/usr/bin/env python3
"""Every number the paper states about the case study must come out of the model.

Run after building: it re-runs the model and checks the built PDF's text against it.
"""
import re, subprocess, sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis_model as m

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf = os.path.join(ROOT, "paper", "CCE-R9-20260827_From-Q-Day-to-Exposure-Curves.pdf")
text = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
flat = re.sub(r"\s+", " ", text)

rows, optima = m.table()
checks, bad = [], 0

for r in rows:
    for val in (r[2], r[3], r[4]):
        checks.append(("%s / %s" % (r[0], r[1]), "%.2f" % val))
checks.append(("historical", "%.2f" % m.hndl(range(6), m.clocks("Fast-first")[2],
                                             m.T_HIST, m.T0, historical=True)))
for mult in (1, 2, 5, 10):
    w = [x * mult for x in m.KNAPSACK_WORK]
    checks.append(("knapsack %dx" % mult,
                   "%.1f" % m.knapsack(m.KNAPSACK_VALUES, w, m.KNAPSACK_BUDGET)))
for r in rows:
    if r[6] is not None:
        checks.append(("%s / %s pct" % (r[0], r[1]), "%.1f" % abs(r[6])))

for what, val in checks:
    ok = val in flat
    if not ok: bad += 1
    print("%-4s %-34s %s" % ("OK" if ok else "MISS", what, val))

# the two optimal orders must be stated as the model finds them
for scen, o in optima.items():
    names = [m.SYSTEMS[i][0] for i in o]
    print("%-4s %-34s %s" % ("--", scen + " optimum", " -> ".join(names)))

print("\n%d checks, %d not found in the PDF" % (len(checks), bad))
sys.exit(1 if bad else 0)
