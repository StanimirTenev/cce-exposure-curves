#!/usr/bin/env python3
"""Build the checklist in both forms from one source.

The Markdown is what GitHub renders; the PDF is what someone prints and writes on.
They are generated from the same data here so they cannot drift apart -- a checklist
whose two versions disagree is worse than one version.

  python3 checklist/build.py     # writes CHECKLIST.md and checklist/checklist.pdf
"""
import os, shutil, subprocess, sys, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "checklist")

TITLE = "Ten questions to ask before you fix a migration order"
VERSION = "v1 · 28 August 2026"

INTRO = [
    "A short companion to the migration guidance you are already required to follow. It does "
    "not replace it. NIST SP 1800-38, the NCSC roadmap, ETSI TR 103 619, Singapore's "
    "Quantum-Safe Handbook and the FS-ISAC roadmap all tell you to inventory, prioritise, then "
    "migrate. This covers the prioritise step, which is where those documents say the least and "
    "where the consequences of getting it wrong are largest.",
    "Each question wants a number or a name. None of them is a yes/no. A checklist answered "
    "“yes, we have that” is a checklist that has told you nothing.",
]

SECTIONS = [
    ("Before you order anything", [
        ("For what share of the systems your scan found do you have a stated confidentiality "
         "lifetime?",
         "Not “do we have a data classification policy” — what fraction of the "
         "estate that policy actually reaches. The answer is a percentage.",
         "Good: “412 of 690 locations, 60%.”   Bad: “we classify our data.”"),
        ("Which systems have no entry? Name them.",
         "This is the denominator. An ordering computed over the classified part is not an "
         "ordering over the estate, and the difference is invisible unless someone writes it "
         "down.", None),
    ]),
    ("On the order itself", [
        ("Is your order derived from something measured, or from a criticality register?",
         "Most published guidance says to start with the most critical systems, and criticality "
         "registers are usually inherited from an older risk process. Ask what measurement, if "
         "any, sits underneath.", None),
        ("Does your order change if the capability arrives in 2035 rather than 2045?",
         "If the answer is no, the order is not conditioned on anything about the threat. It is "
         "a ranking of your present opinion of your own systems, which is a different object.",
         None),
        ("For each of your top ten: what is the confidentiality lifetime, and what is the "
         "emission rate?",
         "The second one is usually missing. A system that emits a small volume of long-lived "
         "data can matter more than one holding a large volume of short-lived data, and "
         "criticality does not see the difference.", None),
    ]),
    ("The part migration does not fix", [
        ("Which systems have a required confidentiality lifetime longer than any assumption you "
         "would defend in front of an auditor?",
         "Thirty-year retention protected by an assumption most people would defend for ten is "
         "not a migration problem. Migrating it changes which conjecture you rely on, not how "
         "long you need the answer to hold.", None),
        ("For those, what is the plan other than migration?",
         "There are three, and none is a new algorithm: retain the data for less time, split the "
         "secret so that no single location holds it, or do not collect it. All three are "
         "unfashionable and all three are cheaper.", None),
        ("Have you estimated what has already left?",
         "Migration protects future emission. It does nothing for data already captured. If "
         "harvest-now-decrypt-later is in your threat model — Singapore's handbook names "
         "long-lived records as the primary target — the volume already gone is part of the "
         "answer, and it does not shrink.", None),
    ]),
    ("The evidence underneath", [
        ("Can you show the date and scope of the inventory the plan rests on?",
         "Scope means what was looked at and what was not: source, CI, infrastructure-as-code, "
         "runtime, hardware, third parties. A plan built on an inventory of unstated scope "
         "inherits that silence.", None),
        ("Does your scanner report what it could not read?",
         "Ask for the number of targets it attempted and failed to open — permission errors, "
         "binaries with no symbols, containers it could not enter, repositories it lacked a token "
         "for. If the tool cannot answer, “no findings” and “nothing "
         "vulnerable” are the same sentence in your report, and they are not the same fact.",
         None),
    ]),
]

WHY = [
    ("Why the order matters more than it looks",
     "The guidance converges on ordering by criticality: NIST triages critical business "
     "processes first, the NCSC roadmap's 2031 milestone is the “most critical assets”, "
     "PMMP groups by risk and process. Singapore's handbook is the most careful of them — it "
     "names IT systems with long-lived data as primary harvest-now-decrypt-later targets and asks "
     "for impact mapped against likelihood. Even there, long-lived data is a category to include "
     "among the crown jewels rather than a quantity to order by."),
    (None,
     "There is a result about this. No ordering built only on a system's present criticality can "
     "minimise capability-conditioned exposure for all capability distributions, shelf lives, "
     "emission rates, durations and objective weights. It is not that criticality-first is a poor "
     "heuristic; it is that no static ranking of present properties can be optimal across the "
     "instances an organisation might actually be in, because the optimal order depends on those "
     "quantities jointly."),
    (None,
     "Proposition 3, in From Q-Day to Exposure Curves: https://doi.org/10.5281/zenodo.22126410"),
    ("What this checklist is not",
     "It does not tell you what your order should be, and it produces no score, rating or risk "
     "level. It is a set of questions whose answers you should have before you defend an order to "
     "anyone. If several of them cannot be answered today, that is the finding, and it is a more "
     "useful one than a number would have been."),
]


LATEX_HEAD = r"""\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=17mm,top=15mm,bottom=14mm]{geometry}
\usepackage{lmodern}
\usepackage[hidelinks]{hyperref}
\usepackage{parskip}
\usepackage{titlesec}
\usepackage{fancyhdr}
\setlength{\parindent}{0pt}
\titleformat{\section}{\bfseries\large}{}{0pt}{}[\vspace{-6pt}\rule{\linewidth}{0.4pt}]
\titlespacing{\section}{0pt}{10pt}{4pt}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\scriptsize\color{gray}CC BY 4.0 $\cdot$ github.com/StanimirTenev/cce-exposure-curves}
\fancyfoot[R]{\scriptsize\color{gray}\thepage\ of \pageref{LastPage}}
\usepackage{lastpage}
\usepackage{xcolor}
\newcommand{\ansbox}{\vspace{2pt}\fbox{\parbox[t][22pt][t]{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{%
  \scriptsize\color{gray}answer}}\par\vspace{4pt}}
\begin{document}
"""


def _tex(t):
    """Escape for LaTeX and turn the typographic characters into their macros."""
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        t = t.replace(a, b)
    return (t.replace("“", "``").replace("”", "''")
             .replace("’", "'").replace("—", "---").replace("–", "--"))


def build_tex():
    p = [LATEX_HEAD]
    p.append(r"{\LARGE\bfseries %s}\par" % _tex(TITLE))
    p.append(r"{\small\color{gray}%s}\par\vspace{6pt}" % _tex(VERSION))
    p.append(r"{\small %s\par}" % _tex(INTRO[0]))
    p.append(r"\vspace{4pt}\fcolorbox{gray}{gray!8}{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}"
             r"{\small %s}}\vspace{4pt}" % _tex(INTRO[1]))
    n = 0
    for title, items in SECTIONS:
        if title.startswith("The part migration"):
            p.append(r"\newpage")
        p.append(r"\section*{%s}" % _tex(title))
        for q, gl, ex in items:
            n += 1
            p.append(r"\textbf{%d.\ %s}\par" % (n, _tex(q)))
            p.append(r"{\small\color{black!70} %s\par}" % _tex(gl))
            if ex:
                p.append(r"{\footnotesize\itshape\color{black!55} %s\par}" % _tex(ex))
            p.append(r"\ansbox")
    p.append(r"\newpage")
    for head, body in WHY:
        if head:
            p.append(r"\section*{%s}" % _tex(head))
        p.append(r"{\small %s\par}" % _tex(body))
    p.append(r"\end{document}")
    return "\n".join(p)


def _wrap(t, width=95):
    """Wrapped so the raw file reads as well as the rendered one."""
    return "\n".join(textwrap.wrap(t, width=width)) if t else t


def build_md():
    out = [f"# {TITLE}", ""]
    out += [_wrap(INTRO[0]), "", _wrap(f"**{INTRO[1]}**"), "", "---", ""]
    n = 0
    for title, items in SECTIONS:
        out += [f"## {title}", ""]
        for q, gl, ex in items:
            n += 1
            out += [_wrap(f"**{n}. {q}**"), "", _wrap(gl), ""]
            if ex:
                out += [_wrap(f"*{ex}*"), ""]
    out += ["---", ""]
    for head, body in WHY:
        if head:
            out += [f"## {head}", ""]
        out += [_wrap(body), ""]
    out += ["---", "",
            _wrap("*CC BY 4.0. Part of "
            "[cce-exposure-curves](https://github.com/StanimirTenev/cce-exposure-curves). "
            "A typeset version with space to write the answers is in "
            "[checklist/checklist.pdf](checklist/checklist.pdf).*"), ""]
    return "\n".join(out)


def _page_ink(png):
    """Fraction of sampled pixels that are not near-white."""
    from PIL import Image
    im = Image.open(png).convert("L")
    w, h = im.size
    px = im.load()
    pts = [(x, y) for y in range(0, h, 4) for x in range(0, w, 4)]
    return sum(1 for x, y in pts if px[x, y] < 200) / len(pts)


def _drop_blank_last_page(pdf):
    """LibreOffice's HTML import emits a trailing empty page here regardless of margins.
    Rather than tune CSS until it happens not to, measure the last page and drop it if it
    carries no ink. A blank page at the end of a document someone prints is the kind of
    small wrongness that makes the rest look unchecked."""
    import glob, tempfile
    n = int(subprocess.run(["pdfinfo", pdf], capture_output=True, text=True
                           ).stdout.split("Pages:")[1].split()[0])
    if n < 2:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-png", "-r", "50", "-f", str(n), "-l", str(n),
                        pdf, os.path.join(tmp, "p")], check=True, capture_output=True)
        last = sorted(glob.glob(os.path.join(tmp, "p-*.png")))
        if not last or _page_ink(last[0]) > 0.001:
            return False
        subprocess.run(["pdfseparate", "-f", "1", "-l", str(n - 1), pdf,
                        os.path.join(tmp, "s-%d.pdf")], check=True, capture_output=True)
        parts = sorted(glob.glob(os.path.join(tmp, "s-*.pdf")),
                       key=lambda f: int(f.rsplit("-", 1)[1].split(".")[0]))
        subprocess.run(["pdfunite"] + parts + [pdf], check=True, capture_output=True)
    return True


def main():
    open(os.path.join(ROOT, "CHECKLIST.md"), "w", encoding="utf-8").write(build_md())
    tex = os.path.join(HERE, "checklist.tex")
    open(tex, "w", encoding="utf-8").write(build_tex())
    if not shutil.which("pdflatex"):
        print("CHECKLIST.md and checklist.tex written; no pdflatex, PDF skipped")
        return 0
    for _ in range(2):   # twice, so \pageref{LastPage} settles
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", HERE, tex],
                       check=False, capture_output=True)
    for ext in (".aux", ".log", ".out"):
        f = os.path.join(HERE, "checklist" + ext)
        if os.path.exists(f):
            os.remove(f)
    print("written: CHECKLIST.md, checklist/checklist.tex, checklist/checklist.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
