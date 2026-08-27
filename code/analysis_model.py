#!/usr/bin/env python3
"""CCE case study: inputs, 720-schedule enumeration, figures and machine-readable results.

Rebuilt August 2026 after the original script was lost. Every input is the one printed in
the paper. Integration is by midpoint rule on a half-month grid throughout; no random
sampling is used, so results are deterministic.

Both Stieltjes integrals include capability that has already arrived at the lower limit:
a system is exposed if the capability exists at t_0, and captured data is decryptable if
the capability preceded capture. See Sections 3.1 and 3.2.
"""
import csv, itertools, json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results")
FIGS = os.path.join(ROOT, "paper", "figures")

T0, T_END, T_HIST, START = 2026.0, 2060.0, 2021.0, 2027.0
STEP = 1.0 / 24.0

SYSTEMS = [
    # name, duration, criticality, live value, HNDL rate, shelf life, class
    ("Transaction signing",    1.5, 5, 100, 1.0,  0.5, "fast"),
    ("Genomic exchange",       3.0, 4,  25, 9.0, 35.0, "any"),
    ("M&A data rooms",         1.0, 4,  15, 6.0, 20.0, "any"),
    ("Code-signing service",   2.0, 5,  80, 1.5, 15.0, "any"),
    ("Customer identity API",  2.0, 3,  35, 7.0,  8.0, "fast"),
    ("Operational telemetry",  1.0, 2,   8, 14.0, 1.0, "any"),
]
SCEN = {  # (fast clock, slow clock) as (location, scale, ceiling)
    "Fast-first": ((2039.0, 3.4, 0.86), (2045.0, 3.8, 0.82)),
    "Slow-first": ((2045.0, 3.8, 0.82), (2039.0, 3.4, 0.86)),
}
KNAPSACK_VALUES = (40, 30, 24, 18, 12, 8)
KNAPSACK_WORK = (40, 25, 18, 12, 8, 5)
KNAPSACK_BUDGET = 60


def logistic(loc, scale, ceiling):
    return lambda t: ceiling / (1.0 + math.exp(-(t - loc) / scale))


def clocks(scen):
    fast = logistic(*SCEN[scen][0])
    slow = logistic(*SCEN[scen][1])
    any_ = lambda t: 1.0 - (1.0 - fast(t)) * (1.0 - slow(t))
    return fast, slow, {"fast": fast, "any": any_}


def spans(order):
    out, clock = {}, START
    for idx in order:
        out[idx] = (clock, clock + SYSTEMS[idx][1])
        clock += SYSTEMS[idx][1]
    return out


def residual(order):
    sp = spans(order)
    def R(i, t):
        a, b = sp[i]
        if t <= a: return 1.0
        if t >= b: return 0.0
        return 1.0 - (t - a) / (b - a)
    return R


def midpoints(lo, hi):
    n = int(round((hi - lo) / STEP))
    return [(lo + (k + 0.5) * STEP, lo + k * STEP, lo + (k + 1) * STEP) for k in range(n)]


def live(order, F):
    """Capability already present at t_0 exposes every system at its residual there (=1)."""
    R = residual(order)
    total = sum(row[3] * F[row[6]](T0) for row in SYSTEMS)
    for t, a, b in midpoints(T0, T_END):
        for i, row in enumerate(SYSTEMS):
            total += row[3] * R(i, t) * (F[row[6]](b) - F[row[6]](a))
    return total


def hndl(order, F, lo=T0, hi=T_END, historical=False):
    R = residual(order)
    anyc = F["any"]
    total = 0.0
    for u, _a, _b in midpoints(lo, hi):
        for i, row in enumerate(SYSTEMS):
            r = 1.0 if historical else R(i, u)
            total += row[4] * r * anyc(u + row[5]) * STEP
    return total


POLICIES = {
    "Criticality-first":  lambda: sorted(range(6), key=lambda i: (-SYSTEMS[i][2], -SYSTEMS[i][3])),
    "Shelf-life score":   lambda: sorted(range(6), key=lambda i: -(SYSTEMS[i][4] * SYSTEMS[i][5])),
    "Live-value first":   lambda: sorted(range(6), key=lambda i: -SYSTEMS[i][3]),
    "Shortest-job first": lambda: sorted(range(6), key=lambda i: (SYSTEMS[i][1], -SYSTEMS[i][2])),
}


def knapsack(values, works, budget):
    order = sorted(range(len(values)), key=lambda j: -values[j] / works[j])
    got, left = 0.0, float(budget)
    for j in order:
        take = min(1.0, left / works[j])
        got += take * values[j]
        left -= take * works[j]
        if left <= 1e-12: break
    return got


def table():
    rows, optima = [], {}
    for scen in SCEN:
        _f, _s, F = clocks(scen)
        for pol, fn in POLICIES.items():
            o = fn()
            L, H = live(o, F), hndl(o, F)
            rows.append([scen, pol, L, H, L + H, [SYSTEMS[i][0] for i in o]])
        best = min(((live(o, F) + hndl(o, F), o) for o in itertools.permutations(range(6))),
                   key=lambda z: z[0])
        o = best[1]
        rows.append([scen, "Optimised", live(o, F), hndl(o, F), best[0],
                     [SYSTEMS[i][0] for i in o]])
        optima[scen] = o
    base = {s: next(r[4] for r in rows if r[0] == s and r[1] == "Criticality-first") for s in SCEN}
    for r in rows:
        r.append(None if r[1] == "Criticality-first" else 100.0 * (r[4] - base[r[0]]) / base[r[0]])
    return rows, optima


def figures(rows, optima):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(FIGS, exist_ok=True)
    grid_t = [T0 + k * STEP for k in range(int((T_END - T0) / STEP) + 1)]

    def save(fig, name):
        for ext in ("pdf", "png"):
            fig.savefig(os.path.join(FIGS, f"{name}.{ext}"), bbox_inches="tight", dpi=150)
        plt.close(fig)

    fast, slow, F = clocks("Fast-first")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(grid_t, [fast(t) for t in grid_t], label="fast clock (2039, 3.4, ceiling 0.86)")
    ax.plot(grid_t, [slow(t) for t in grid_t], "--", label="slow clock (2045, 3.8, ceiling 0.82)")
    ax.plot(grid_t, [F["any"](t) for t in grid_t], ":", label="any platform")
    ax.set_xlabel("year"); ax.set_ylabel("cumulative probability"); ax.set_ylim(0, 1)
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    save(fig, "fig_cdfs")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, scen in zip(axes, SCEN):
        sel = [r for r in rows if r[0] == scen]
        labels = [r[1].replace(" ", "\n") for r in sel]
        ax.bar(labels, [r[2] for r in sel], label="live")
        ax.bar(labels, [r[3] for r in sel], bottom=[r[2] for r in sel], label=r"future $H_{sep}$")
        ax.set_title(scen, fontsize=10); ax.tick_params(labelsize=7); ax.grid(axis="y", alpha=.3)
    axes[0].set_ylabel("separable benchmark"); axes[0].legend(fontsize=8)
    save(fig, "fig_policy_comparison")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, scen in zip(axes, SCEN):
        _f, _s, F = clocks(scen)
        pts = [(live(o, F), hndl(o, F)) for o in itertools.permutations(range(6))]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=6, alpha=.35)
        o = optima[scen]
        ax.scatter([live(o, F)], [hndl(o, F)], s=60, marker="*", zorder=3, label="equal-weight optimum")
        ax.set_xlabel("live exposure"); ax.set_title(scen, fontsize=10)
        ax.grid(alpha=.3); ax.legend(fontsize=8)
    axes[0].set_ylabel(r"future $H_{sep}$")
    save(fig, "fig_pareto")

    _f, _s, F = clocks("Fast-first")
    o = optima["Fast-first"]; R = residual(o)
    tot_v = sum(r[3] for r in SYSTEMS); tot_h = sum(r[4] for r in SYSTEMS)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.plot(grid_t, [sum(SYSTEMS[i][3] * R(i, t) for i in range(6)) / tot_v for t in grid_t],
            label="live residual (value-weighted)")
    ax.plot(grid_t, [sum(SYSTEMS[i][4] * R(i, t) for i in range(6)) / tot_h for t in grid_t],
            "--", label="vulnerable emission (rate-weighted)")
    ax.set_xlim(T0, 2040); ax.set_xlabel("year"); ax.set_ylabel("fraction remaining")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    save(fig, "fig_trajectories")

    budgets = [b for b in range(0, 121, 2)]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    for mult, style in ((1, "-"), (2, "--"), (5, "-."), (10, ":")):
        w = [x * mult for x in KNAPSACK_WORK]
        ax.plot(budgets, [knapsack(KNAPSACK_VALUES, w, b) for b in budgets], style,
                label=f"{mult}x work")
    ax.axvline(KNAPSACK_BUDGET, color="grey", lw=.8)
    ax.set_xlabel("adversary work budget"); ax.set_ylabel("realisable archived value")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    save(fig, "fig_budget")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, optima = table()
    hist = hndl(range(6), clocks("Fast-first")[2], T_HIST, T0, historical=True)

    with open(os.path.join(OUT, "results.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "policy", "live", "future_H_sep", "benchmark_total",
                    "vs_criticality_pct", "schedule"])
        for r in rows:
            w.writerow([r[0], r[1], f"{r[2]:.2f}", f"{r[3]:.2f}", f"{r[4]:.2f}",
                        "" if r[6] is None else f"{r[6]:.1f}", " -> ".join(r[5])])
    with open(os.path.join(OUT, "inputs.json"), "w") as fh:
        json.dump({"systems": [dict(zip(
            ["name", "duration", "criticality", "live_value", "hndl_rate", "shelf_life", "class"], s))
            for s in SYSTEMS], "scenarios": SCEN, "grid_step_years": STEP,
            "horizon": [T0, T_END], "historical_window": [T_HIST, T0],
            "migration_start": START, "knapsack": {"values": KNAPSACK_VALUES,
            "work": KNAPSACK_WORK, "budget": KNAPSACK_BUDGET}}, fh, indent=1)

    for r in rows:
        print("%-11s %-19s %8.2f %8.2f %8.2f %s" %
              (r[0], r[1], r[2], r[3], r[4], "" if r[6] is None else "%+.1f%%" % r[6]))
    print("historical separable HNDL (invariant): %.2f" % hist)
    for m_ in (1, 2, 5, 10):
        print("knapsack at budget %d, %dx work: %.1f" %
              (KNAPSACK_BUDGET, m_, knapsack(KNAPSACK_VALUES, [x * m_ for x in KNAPSACK_WORK], KNAPSACK_BUDGET)))
    for scen, o in optima.items():
        print("%s optimum: %s" % (scen, " -> ".join(SYSTEMS[i][0] for i in o)))
    figures(rows, optima)
    print("figures written to", FIGS)


if __name__ == "__main__":
    main()
