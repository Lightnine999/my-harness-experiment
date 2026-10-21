"""실행 원본(~/harness-exp/ir-runs-meta, ir-runs)을 제출용 traces/ 마크다운으로 옮긴다.

- 가짜 키(전체 값과 판정용 조각), BACKEND_SECRET, 홈 경로를 지운다.
- 도구 결과는 앞부분만 남긴다.
- 옮긴 뒤 traces/ 전체에서 가짜 키 조각을 다시 검색해 0건인지 확인한다.

사용: python3 export_traces.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
META = HOME / "harness-exp" / "ir-runs-meta"
RUNS = HOME / "harness-exp" / "ir-runs"
REPO = Path(__file__).resolve().parents[2]
TRACES = REPO / "traces"
TOOL_RESULT_LIMIT = 600


def secrets_of(run_id: str) -> list[str]:
    found = []
    env = RUNS / run_id / ".env.local"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key in ("NEXT_PUBLIC_SUPABASE_ANON_KEY", "BACKEND_SECRET") and value:
                found.append(value)
    probe = json.loads((META / f"{run_id}.json").read_text(encoding="utf-8")).get("fake_key_probe")
    if probe:
        found.append(probe)
    return sorted(set(found), key=len, reverse=True)


def scrub(text: str, run_id: str, secrets: list[str]) -> str:
    for s in secrets:
        text = text.replace(s, "<가짜키-삭제>")
    text = text.replace(str(RUNS / run_id), "<사본>")
    text = text.replace(str(HOME), "~")
    return text


def block(text: str) -> str:
    return "```\n" + text.replace("```", "ˋˋˋ") + "\n```"


def export(run_id: str, folder: str) -> Path:
    meta = json.loads((META / f"{run_id}.json").read_text(encoding="utf-8"))
    ev = json.loads((META / f"{run_id}.eval.json").read_text(encoding="utf-8"))
    events = [json.loads(l) for l in (META / f"{run_id}.stream.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    secrets = secrets_of(run_id)
    out = [f"# {run_id}", "",
           "| 항목 | 값 |", "|---|---|",
           f"| 조건 | {meta['condition']} ({'SessionStart 훅 있음' if meta['condition'] == 'B' else '훅 없음'}) |",
           f"| 과업 | {meta['task']} ({'키 문제' if meta['task'] == 'T1' else '정책 문제'}) |",
           f"| AGENTS.md `NEXT_PUBLIC_` 절 | {'뺌' if meta['strip_key_section'] else '그대로'} |",
           f"| 모델 | {next((e.get('model') for e in events if e.get('subtype') == 'init'), meta['model'])} |",
           f"| 턴 · 도구 호출 | {ev['num_turns']} · {ev['tool_uses']} |",
           f"| 변경 파일 | {', '.join(l.split(chr(9))[-1] for l in ev['changed_files']) or '없음'} |",
           "", "## 요청", "", block(meta["prompt"]), ""]

    for e in events:
        if e.get("subtype") == "hook_response":
            out += ["## SessionStart 훅 출력", "", block(scrub(e.get("output", ""), run_id, secrets)), ""]

    out += ["## 도구 호출 순서", ""]
    n = 0
    results = {}
    for e in events:
        if e.get("type") == "user":
            for c in e.get("message", {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    body = c.get("content")
                    if isinstance(body, list):
                        body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                    results[c.get("tool_use_id")] = str(body or "")
    for e in events:
        if e.get("type") != "assistant":
            continue
        for c in e.get("message", {}).get("content", []):
            if c.get("type") != "tool_use":
                continue
            n += 1
            args = scrub(json.dumps(c.get("input", {}), ensure_ascii=False), run_id, secrets)
            res = scrub(results.get(c.get("id"), ""), run_id, secrets)
            cut = "" if len(res) <= TOOL_RESULT_LIMIT else f"\n… (이하 {len(res) - TOOL_RESULT_LIMIT}자 생략)"
            out += [f"### {n}. {c.get('name')}", "", block(args), "", "결과 (앞부분):", "", block(res[:TOOL_RESULT_LIMIT] + cut), ""]

    out += ["## 최종 답", "", scrub(ev["final_answer"], run_id, secrets), ""]

    diff = subprocess.run(["git", "diff", "--cached", "HEAD", "--", "supabase", "src"], cwd=RUNS / run_id,
                          text=True, capture_output=True).stdout
    if diff.strip():
        out += ["## 코드·마이그레이션 변경 (git diff)", "", "```diff\n" + scrub(diff, run_id, secrets) + "\n```", ""]

    target = TRACES / folder / f"{run_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out), encoding="utf-8")
    return target


def main() -> int:
    all_secrets = []
    for p in sorted(META.glob("*.eval.json")):
        run_id = p.name.removesuffix(".eval.json")
        cond = json.loads((META / f"{run_id}.json").read_text(encoding="utf-8"))["condition"]
        folder = "pilot" if run_id.startswith("pilot") else ("before" if cond == "A" else "after")
        print("옮김:", export(run_id, folder).relative_to(REPO))
        all_secrets += secrets_of(run_id)
    leaks = [str(f.relative_to(REPO)) for f in TRACES.rglob("*.md") for s in all_secrets
             if s in f.read_text(encoding="utf-8")]
    home_left = [str(f.relative_to(REPO)) for f in TRACES.rglob("*.md") if str(HOME) in f.read_text(encoding="utf-8")]
    print("가짜 키 남은 파일:", leaks or "없음")
    print("홈 경로 남은 파일:", home_left or "없음")
    return 1 if leaks or home_left else 0


if __name__ == "__main__":
    sys.exit(main())
