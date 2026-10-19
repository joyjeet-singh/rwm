#!/bin/zsh
# Round-5 launcher: one fresh Claude Code session per section of PLAN.md.
#   docs/presubmission/round5/go.zsh G3          start session G3
#   docs/presubmission/round5/go.zsh G3 resume   resume a PARTIAL or BLOCKED G3
emulate -L zsh
set -euo pipefail
cd "${0:A:h:h:h:h}"                      # the repository root
sid=${1:?"usage: go.zsh SESSION [resume], e.g. go.zsh G3"}
typeset -A model effort
model=(G0 claude-sonnet-5-5 G1 claude-sonnet-5-5 G2 claude-opus-5-5 GT1 claude-opus-5-5
       G3 claude-opus-5-5 G4 claude-sonnet-5-5 G5 claude-opus-5-5 G6 claude-sonnet-5-5
       G7 claude-sonnet-5-5 G8 claude-opus-5-5 G9 claude-sonnet-5-5 G10 claude-sonnet-5-5
       G11 claude-opus-5-5 G12 claude-opus-5-5 GT2 claude-sonnet-5-5 G13 claude-opus-5-5
       G14 claude-opus-5-5 G15 claude-opus-5-5 G16 claude-opus-5-5 G17 claude-opus-5-5
       G18 claude-sonnet-5-5)
effort=(G0 medium G1 high G2 high GT1 high G3 high G4 high G5 medium G6 high G7 medium
        G8 high G9 medium G10 high G11 high G12 high GT2 medium G13 high G14 medium
        G15 medium G16 high G17 medium G18 medium)
[[ -n ${model[$sid]:-} ]] || { print -u2 "unknown session: $sid"; exit 2; }
plan=docs/presubmission/round5/PLAN.md
if [[ ${2:-} == resume ]]; then
  ask="Read $plan §1, the section for session $sid and docs/presubmission/round5/CHECKPOINT.md, then resume session $sid."
else
  ask="Read $plan §1 and the section for session $sid, then carry out session $sid."
fi
excl='{"claudeMdExcludes":["'"$HOME"'/Downloads/CLAUDE.md"]}'
exec claude --model "${model[$sid]}" --effort "${effort[$sid]}" --name "round5-$sid" \
  --settings "$excl" "$ask"
