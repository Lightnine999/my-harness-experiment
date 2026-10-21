"""본 실행 12회를 순서대로 준비·실행·채점한다. 조건 순서 효과를 줄이려고 A/B와 T1/T2를 섞어 돌린다."""

import subprocess
import sys
from pathlib import Path

TRIAL = Path(__file__).with_name("trial.py")
ORDER = [
    (rep, cond, task)
    for rep in (1, 2, 3)
    for cond, task in (("A", "T1"), ("B", "T2"), ("B", "T1"), ("A", "T2"))
]

for rep, cond, task in ORDER:
    rid = f"main-{cond}-{task}-r{rep}"
    print(f"=== {rid}", flush=True)
    for step in (["prepare", rid, cond, task, "--strip-key-section"], ["run", rid], ["evaluate", rid]):
        proc = subprocess.run([sys.executable, str(TRIAL), *step], text=True, capture_output=True)
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
        print(f"  {step[0]}: exit={proc.returncode} {' | '.join(tail)[:300]}", flush=True)
        if proc.returncode != 0 and step[0] != "run":
            break
print("=== 완료", flush=True)
