"""R7: the small fixes from the fresh-eyes review (PLAN round 3, R7 step 5), each three sentences or fewer.
round3/REVIEW.md lists every finding and which edit here answers it. The matcher, the exactly-once assertions and the
.bak discipline are r2_patch.py's, imported. Usage, from the repository root:
    $PY docs/presubmission/round3/r7_patch.py <item>
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply  # noqa: E402

BAK = "/Users/Shared/rwm_verify/evidence/R3R7"
ITEMS = {
    # Step 1, the whole read: summaries stronger than their sections.
    "body": ("PAPER.template.md", [
        # B1, §1: §5 finds the training claim at long horizons and reversed at one step
        ("and test the central training claim, which holds.",
         "and test the central training claim, which holds at long horizons."),
        # B2, §2, and B3, §6.4: §6.8 and §11 say the independent ensemble bounds sharing's cost, not measures it
        ("with the sharing quantified at {{v1_shared_pct}}% of each member and the cost measured at "
         "{{m44_ratio_gain}}× (§6.8).",
         "with the sharing quantified at {{v1_shared_pct}}% of each member and its cost bounded by the "
         "{{m44_ratio_gain}}× an independent ensemble gains (§6.8)."),
        ("with the sharing quantified at {{v1_shared_pct}}% of each member and the cost measured at "
         "{{m44_ratio_gain}}× on the overconfidence factor (§6.8).",
         "with the sharing quantified at {{v1_shared_pct}}% of each member and its cost bounded by the "
         "{{m44_ratio_gain}}× an independent ensemble gains on the overconfidence factor (§6.8)."),
        # B4, §6.1: §6.5 finds the ordering weaker than it looks per dimension, §6.6 a free signal close behind
        ("Our measurement **supports the first claim**: the epistemic ordering is real and strong.",
         "Our measurement **supports the first claim**: the epistemic ordering is real (§6.6), though weaker per "
         "dimension than it looks (§6.5)."),
        # B5, §5: the training horizon, h = 8, resolves; the unresolved point is h = 1, inside it
        ("and the claim is weakest exactly where the model is trained.",
         "and the claim is weakest inside the horizon the model is trained on."),
        # B6, §10: §11 gives the proxy's caveats; the summary dropped them
        ("leaves every pairwise ordering of accumulated penalty unchanged on the available trajectories (§11).",
         "leaves every pairwise ordering of accumulated penalty unchanged on the available trajectories, a test "
         "whose null is partly structural (§11)."),
        # Annex 4 item 11, ruling V7: two sentences, the facts kept and the invitation dropped
        ("**On anonymity, stated rather than implied.** The code and data for this work are public, as they are for "
         "most reproducibility work, and a reviewer who chooses to look can identify the author. The submission is "
         "anonymised — the bundle is scrubbed and asserted clean of a deny-list, and the files that carry identity are "
         "excluded from it — but that is anonymity of the *submission*, not unfindability of the work. Making the "
         "repository private would remove the identifying link and also remove the checkability §8 depends on, which "
         "is the worse trade. The decision and its reasoning are recorded in `docs/DOUBLE_BLIND_DECISION.md`.",
         "**On anonymity.** The code and data for this work are public, as they are for most reproducibility work, "
         "and the submission is anonymised: its bundle is scrubbed, asserted clean of a deny-list, and excludes the "
         "files that carry identity. Why the repository stays public, which §8's checkability depends on, is recorded "
         "in `docs/DOUBLE_BLIND_DECISION.md`."),
    ]),
    # Step 2, agent 1 (Appendices A-L), each verified against the source before this edit (REVIEW.md, A1-A7).
    "agents": ("PAPER.template.md", [
        # A1, Appendix B: the rate is fitted on 22 of the 28; the 28 are the family
        ("They are **not** part of the {{n_runs}} runs §6.3 fits the σ-collapse rate over,",
         "They are **not** part of the {{n_runs}} runs of §6.3's σ-collapse family,"),
        # A2, §6.3, and A3, Appendix J: the 5 gaussian_nll runs of the 28 rise; each objective is linear and tight
        ("then observed it: across all {{n_runs}} runs at the released width outside §5.2's sweep the collapse is "
         "linear in iteration count and its rate is nearly identical (Figure 4a).",
         "then observed it: across all {{n_runs}} runs at the released width outside §5.2's sweep the log-σ range "
         "moves linearly in iteration count at a nearly identical rate within each objective, falling under sampled "
         "MSE and rising under the corrected one (Figure 4a)."),
        ("Across all {{n_runs}} runs of that family the collapse is linear in iteration count and its rate is nearly "
         "identical (Figure 4a).",
         "Across all {{n_runs}} runs of that family the log-σ range moves linearly in iteration count at a nearly "
         "identical rate within each objective, falling under sampled MSE and rising under the corrected one "
         "(Figure 4a)."),
        # A4, Appendix C: 49.8 h is all 33 runs, not one
        ("plus one world-model training run each at our {{rt_hours}} h scale;",
         "plus a world-model training campaign each on the scale of ours, {{rt_runs}} runs in {{rt_hours}} h;"),
        # A5, Appendix E's caption: two of the commits Figure 1 cites changed hash, and the later rules are found by
        # the commit that introduced their ledger heading (appendix_g_rules.py; Data and code says the same)
        ("resolved by commit *subject* rather than by hash — the history was rewritten once and hashes did not "
         "survive it, while subjects did.",
         "never by a stored hash: the first rules' commits are found by *subject*, because the history was rewritten "
         "once and two of the commits Figure 1 cites changed hash (Data and code), and the later rules' by the commit "
         "that introduced their ledger heading."),
        # A6, Appendix H: the caption names what each row carries; the M-84 row its sample
        ("Measurements are at {{iters_main}} training iterations unless a row says otherwise or concerns the "
         "released checkpoint.",
         "Measurements are at {{iters_main}} training iterations unless a row says otherwise or concerns the "
         "released checkpoint, and each row names its arena."),
        ("Arm A's error at h = 8 on its in-sample arena rises by",
         "Arm A's error at h = 8 on its in-sample arena's {{x2_n_ins}} trajectories rises by"),
        # A7, Appendix D's first table: its verdict cells quote figures from the sections they cite
        ("and because \"no quantitative figure\" is itself a finding that deserves to be checkable row by row.",
         "and because \"no quantitative figure\" is itself a finding that deserves to be checkable row by row. Its "
         "verdict cells quote figures from the sections they cite, each on that section's arena, n_independent and "
         "checkpoint; the second table gives them claim by claim."),
        # Agent 1's note: with two tables in Appendix D, three pointers name the first
        ("classification tags in Appendix D's verdict column,",
         "classification tags in the verdict column of Appendix D's first table,"),
        ("**Appendix D gives the full table**, claim by claim,",
         "**Appendix D's first table gives it in full**, claim by claim,"),
        ("Appendix D's table marks {{orig_n_tested}} claims tested",
         "Appendix D's first table marks {{orig_n_tested}} claims tested"),
    ]),
    # A5: the count in Appendix E's caption comes from the key Data and code prints it with
    "agents2": ("PAPER.template.md", [
        ("once and two of the commits Figure 1 cites changed hash (Data and code)",
         "once and {{f1_n_moved_word}} of the commits Figure 1 cites changed hash (Data and code)"),
    ]),
    # A1 follow-up: the reworded clause took the antecedent of "that rate" with it
    "agents3": ("PAPER.template.md", [
        ("of §6.3's σ-collapse family, because that rate is a property of one architecture",
         "of §6.3's σ-collapse family, because §6.3's rate is a property of one architecture"),
    ]),
    # Annex 4 item 10: the README's findings, each no stronger than the paper's
    "readme": ("README.template.md", [
        ("**1 — The base paper's central training claim reproduces, and the advantage grows with horizon.**",
         "**1 — The base paper's central training claim reproduces at long horizons, grows with horizon, and reverses "
         "at one step.**"),
        ("spanning it only at {{a1_spans_zero_at}}.",
         "spanning it only at {{a1_spans_zero_at}}; there, on {{m64_h1_n}} short windows, a second pre-registered rule "
         "finds teacher forcing ahead ({{m64_h1_gap}} {{m64_h1_ci}})."),
        ("{{a2_rdd_ci}}** with realised error, so it is not merely reporting which episode is hard.",
         "{{a2_rdd_ci}}** with realised error, so it is not merely reporting which episode is hard. But the model's "
         "own predicted step size, which needs no ensemble, ranks error nearly as well ({{e7_step_r}} against "
         "{{e7_r_dis}}), by a margin this sample cannot resolve (§6.6)."),
        ("**6 — That mechanism is tested, not merely asserted, and it holds.**",
         "**6 — That mechanism is tested, not merely asserted, and is supported.**"),
        ("properly is worth doing and is not sufficient (§6.8).",
         "properly is worth doing and is not sufficient (§6.8). The independent models also differ in capacity and data "
         "order, so this bounds the sharing effect rather than isolating it; at matched capacity the gain is "
         "{{m49_ratio_gain}}×, below its minimum detectable effect of {{m49_mde_ratio}}× (rule M-49, §11)."),
    ]),
    # Annex 4 item 10: the model card's headline table is relative-L1, which "normalised error" does not say
    "card": ("scripts/build_model_card.py", [
        ('A(f"Normalised error at a {v(\'v2_diag_h\')}-step horizon on held-out episodes, over three "',
         'A(f"Relative-L1 error, the reference\'s own metric, at a {v(\'v2_diag_h\')}-step horizon on held-out '
         'episodes, over three "'),
    ]),
    # Rule 9: the anonymity paragraph's removed sentence goes to the moved list
    "moved": ("docs/BUILD_CHECKS.template.md", [
        ("- **[References]** The bibliography is generated from",
         "- **[Data and code]** The anonymity paragraph said that a reviewer who chooses to look can identify the "
         "author, and argued that making the repository private would remove the identifying link and also the "
         "checkability §8 depends on, the worse trade. Ruling V7 (round 3) cut it to two sentences; the reasoning is in "
         "`docs/DOUBLE_BLIND_DECISION.md`.\n- **[References]** The bibliography is generated from"),
    ]),
}

if __name__ == "__main__":
    item = sys.argv[1]
    path, edits = ITEMS[item]
    os.makedirs(BAK, exist_ok=True)
    text = open(path, encoding="utf-8").read()
    new = apply(text, edits)                     # asserts each match exactly once before anything is written
    shutil.copy(path, f"{BAK}/{os.path.basename(path)}.{item}.bak")
    open(path, "w", encoding="utf-8").write(new)
    print(f"{item}: {len(edits)} edit(s) to {path}; backup in {BAK}")
