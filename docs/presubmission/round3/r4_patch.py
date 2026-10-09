"""R4: the template edits for the small items, one item at a time (PLAN round 3, R4, S1-S17).

The matcher, the exactly-once assertions and the .bak discipline are r2_patch.py's, imported. Usage, from the
repository root:  $PY docs/presubmission/round3/r4_patch.py <item>
"""
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply, insert_after  # noqa: E402

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R4"
ITEMS = {
    # S4: the introduction understated the negative verdicts
    "s4": {"edits": [("one returned \"cannot be settled\", and we report it.",
                      "several returned verdicts against the original or could not settle the question, and we "
                      "report each (Appendix E).")]},
    # S7: Appendix F said the same thing twice; one paragraph, nothing dropped (the pointer to the supplementary
    # arithmetic is already in the appendix's first paragraph)
    "s7": {"edits": [(
        "We report the arithmetic because it is what let us detect the gap at all, not as a charge against the work. "
        "**§7.5's argument in full.** The σ collapse is linear in iteration count and its rate is nearly identical "
        "across our runs (§6.3), which makes it a clock, and read as a clock it puts the checkpoint's variance state "
        "out of reach of a constant-rate run from the released initialisation at the configured learning rate, at "
        "every iteration count the release, the paper and the checkpoint tag state. The first author's account is that "
        "the released repository is several revisions removed from the setup that trained the checkpoint, which "
        "supplies a mechanism, a warm start or a different `log_delta_logstd` initialisation, that would explain it "
        "with no inconsistency at all. So this is a **documentation gap between a release and a run**: common, worth "
        "recording, and much less interesting than an inconsistency. `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`, shipped "
        "as supplementary, gives the arithmetic and the five assumptions it rests on.",
        "The σ collapse is linear in iteration count and its rate is nearly identical across our runs (§6.3), which "
        "makes it a clock, and read as a clock it puts the checkpoint's variance state out of reach of a constant-rate "
        "run from the released initialisation at the configured learning rate, at every iteration count the release, "
        "the paper and the checkpoint tag state. The first author's account is that the released repository is several "
        "revisions removed from the setup that trained the checkpoint, which supplies a mechanism, a warm start or a "
        "different `log_delta_logstd` initialisation, that would explain it with no inconsistency at all. We report the "
        "arithmetic because it is what let us detect the gap at all, not as a charge against the work."),
        ("That is a documentation gap between a release and a run — common, worth recording, and much less "
         "interesting than an inconsistency.",
         "That is a **documentation gap between a release and a run**: common, worth recording, and much less "
         "interesting than an inconsistency.")]},
    # S9: Appendix E's M-69 note, two sentences: the two timestamps, and that both are positive
    "s9": {"edits": [(
        "`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so the rule's lead time "
        "depends on which timestamp is read: {{m69_lead_author}} by that commit's author time, {{m69_lead_regen}} by its "
        "committer time. The table above renders {{m69_lead_pub}}, the value `results/appendix_g_rules.json` holds; a "
        "clean rebuild regenerates that file from git and may store either reading. Both readings are positive, so the "
        "rule reached git before the data that tested it existed on either one, which is what a lead time is here to "
        "establish.",
        "`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so its lead time is "
        "{{m69_lead_author}} by that commit's author time and {{m69_lead_regen}} by its committer time. Both are "
        "positive, so the rule reached git before its data on either reading.")]},
    # S10: 8 episodes have 7 internal boundaries; the subtraction is one row per episode
    "s10": {"edits": [("less one per episode boundary ({{c2_bounds}} of them),",
                       "less one per episode ({{c2_bounds}} of them), since an episode's first row has no "
                       "predecessor,")]},
    # S11: several long-horizon verdicts are "not resolved"; the bootstrap computes them, it does not pass them
    "s11": {"edits": [("Every long-horizon verdict in this paper survives a bootstrap over independent trajectories,",
                       "Every long-horizon verdict in this paper is computed with a bootstrap over independent "
                       "trajectories,")]},
    # S16: the orphaned bold line joins the paragraph it concludes
    "s16": {"edits": [("once the dependence between dimensions is respected.** **The failure is specifically "
                       "magnitude calibration, in both components.**",
                       "once the dependence between dimensions is respected. The failure is specifically magnitude "
                       "calibration, in both components.**")]},
    # S5: the main text's one commit identifier (rule M-23's), glossed where it appears. PAPER.md keeps the real hash
    # and the submitted PDF prints its anonymous label, so the gloss is worded to be true in both renderings, and points
    # to the unnumbered "Data and code" section by name.
    "s5": {"edits": [("(rule M-23, Appendix E; commit `efc35b8`)",
                      "(rule M-23, Appendix E; commit `efc35b8`, in the submitted paper an anonymised commit label; "
                      "see Data and code)")]},
    # S14: 13 repositories looked at, 10 carry the construction, 1 of those trains it against a sampled squared error.
    # The frozen protocol (results/q1_search_protocol.md, section 3) counts only repositories with the construction
    # as "examined" and prescribes the form "Of N repositories examined", so the 13 are "looked at", not "examined".
    "s14": {"edits": [
        ("Of {{q1_n_examined}} public repositories examined, {{q1_n_carry}} carry the construction and "
         "{{q1_n_inherit}} of those trains it",
         "Of {{q1_n_looked}} public repositories the survey looked at, {{q1_n_carry}} carry the construction, the "
         "ones its protocol counts as examined, and {{q1_n_inherit}} of those trains it"),
        ("A further {{q1_n_absent}} repositories lack the construction, among them mainline `rsl_rl`:",
         "The survey looked at {{q1_n_looked}} in all; the other {{q1_n_absent}} lack the construction, so the "
         "protocol does not count them as examined, among them mainline `rsl_rl`:"),
        ("it stopped at {{q1_n_examined}}, and its notes give no reason.",
         "it stopped at {{q1_n_examined}} examined, {{q1_n_looked}} looked at, and its notes give no reason."),
    ]},
    # S13: a "shorter unit" is defined where the text first relies on it, with its counts bound
    "s13": {"edits": [("but on M-64's shorter units, at the same checkpoint and on the same two episodes,",
                       "but on M-64's shorter units, each {{m64_hist_rows}} + h rows long and non-overlapping "
                       "({{m64_units_list}} on these episodes), at the same checkpoint and on the same two episodes,")]},
    # S8: one bibliography note, in the References, reduced to what was checked and the counts (ledger D-35); §2's
    # note and the drafting history of the generated list move to BUILD_CHECKS' moved list (item "s8_moved")
    "s8": {"edits": [
        ("*Every entry cited here and in §5.3 was checked against the paper itself: title, full author list and year "
         "from the arXiv record, venue from the record or, where it names none, from the paper's own first page, and "
         "every sentence we attribute matched verbatim against the paper's text. {{t1_n_verified}} of {{t1_n_refs}} "
         "entries are verified and {{t1_n_frag_ok}} of {{t1_n_frag}} attributed fragments match verbatim, though "
         "{{t1_n_frag_oneword}} of those are single common words whose match verifies nothing about the attribution "
         "(`results/t1_bibliography_verified.json`). No entry was added that was not verified.*", ""),
        ("*Entries {{t1_first_entry_n}}–{{t1_last_entry_n}} are the bibliography of §2 and §5.3, generated from "
         "`results/t1_bibliography_verified.json` rather than listed here — a hand-maintained list of what a paper "
         "cites drifts exactly as a hand-typed count does, and this one had: six entries cited in §2's prose appeared "
         "in no reference entry while the note below claimed all of them verified. Each was checked against the paper "
         "itself: title and full author list from the arXiv record, venue from the record or the paper's first page, "
         "and for any sentence this paper attributes, the sentence matched verbatim against that paper's own text — "
         "{{t1_n_verified}} of {{t1_n_refs}} entries and {{t1_n_frag_ok}} of {{t1_n_frag}} attributed fragments, "
         "{{t1_n_frag_oneword}} of them single common words whose presence the cited paper's subject guarantees, so "
         "their match could not have failed and verifies nothing about the attribution "
         "(`results/t1_bibliography_verified.json`, ledger `D-35`).*",
         "*Entries {{t1_first_entry_n}}–{{t1_last_entry_n}} are the bibliography of §2 and §5.3, generated from "
         "`results/t1_bibliography_verified.json`. Each was checked against the paper itself: title and full author "
         "list from the arXiv record, venue from the record or the paper's first page, and every sentence this paper "
         "attributes matched verbatim against that paper's own text: {{t1_n_verified}} of {{t1_n_refs}} entries and "
         "{{t1_n_frag_ok}} of {{t1_n_frag}} attributed fragments, {{t1_n_frag_oneword}} of them single common words "
         "whose match verifies nothing about the attribution (ledger `D-35`). No entry was added that was not "
         "verified.*"),
    ]},
    # S2: the verdict's label glossed at its first appearance in section 12, Appendix D and Appendix S (section 6.6
    # and Appendices E and K define it; section 3.2's row is glossed in evidence_summary.py)
    "s2": {"edits": [
        ("({{e7_verdict}}). The scale may be repairable per", "({{e7_verdict}}: {{e7_verdict_gloss}}). The scale may be repairable per"),
    ], "regex": [(r"(\| Epistemic \"closely follows the trend of the prediction error\".*?)\(\{\{e7_verdict\}\}\)",
                  r"\1({{e7_verdict}}: {{e7_verdict_gloss}})"),
                 (r"(The more useful finding is asymmetric.*?so the verdict is )\{\{e7_verdict\}\}\.",
                  r"\1{{e7_verdict}} ({{e7_verdict_gloss}}).")]},
    # S3: Figure 1 now plots every rule (paper_figures.py), so section 8 states the counts once, from Appendix E's keys,
    # and section 13 counts the commits the new figure cites, by the M-48 rewrite window the figure records
    "s3": {"edits": [
        ("Figure 1 gives the lead time for {{f4_n_rules}} of them and Appendix E for all {{appG_n_rules}}; "
         "{{f4_n_positive}} of Figure 1's are positive and {{f4_n_negative}} is not. Figure 1 plots the set it was "
         "drawn over; Appendix E adds every rule since.",
         "Figure 1 and Appendix E give the lead time for all {{appG_n_rules}}; {{appG_n_positive}} are positive and "
         "{{appG_n_negative}} is not."),
        ("so **{{f4_n_commits}} of the commits Figure 1 cites keep their identifiers and two do not** — the two whose "
         "data post-dates that file. Timestamps, content and ordering are unchanged; only the hashes moved, and Figure 1 "
         "resolves each rule by its commit subject for that reason.",
         "so **{{f1_n_kept}} of the {{f1_n_cited}} commits Figure 1 cites keep their identifiers and "
         "{{f1_n_moved_word}} do not**: the {{f1_n_moved_word}} made between that file's introduction and the purge. "
         "Timestamps, content and ordering are unchanged; only the hashes moved, and for that reason Figure 1 finds its "
         "first rules' commits by subject and the later ones by the commit that introduced their ledger heading, never "
         "by a stored hash alone."),
    ]},
}


def run(item):
    spec = ITEMS[item]
    text = open(T, encoding="utf-8").read()
    new = apply(text, spec.get("edits", []))
    for rx, repl in spec.get("regex", []):
        new, k = re.subn(rx, repl, new, count=1, flags=re.S)
        assert k == 1, (item, rx[:60])
    for anchor, add in spec.get("inserts", []):
        new = insert_after(new, anchor, add)
    if spec.get("append_before_final_rule"):
        assert new.rstrip().endswith("\n---"), new[-40:]
        new = new.rstrip()[:-3].rstrip("\n") + "\n" + spec["append_before_final_rule"] + "\n---\n"
    kb = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", text))
    ka = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", new))
    os.makedirs(BAK, exist_ok=True)
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"{item}: keys removed {sorted(kb - ka)}; added {sorted(ka - kb)}")
    subprocess.run(["git", "--no-pager", "diff", "--stat", T])


if __name__ == "__main__":
    for it in sys.argv[1:]:
        run(it)
