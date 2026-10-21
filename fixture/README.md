# fixture — 고정한 작업 입력 원본

모든 시행은 아래 입력에서 출발합니다. 시행마다 원본을 **새로 복사**해서 쓰고, 원본은 바꾸지 않습니다.
입력이 같아야 조건 사이의 차이가 작업 난이도가 아니라 **SessionStart 훅 하나** 때문이라고 말할 수 있습니다.

## 1. 기준 저장소

| 항목 | 값 |
|---|---|
| 저장소 | 직접 만든 IR 자료 생성 서비스 `Web_Development` (Next.js 16 + Supabase) |
| 고정 커밋 | `4552c90` |
| 사본 만드는 법 | `git worktree add --detach ~/harness-exp/ir-base 4552c90` → 시행마다 `git archive`로 풀어 **새 git 저장소**로 만듦 (원본 커밋 이력은 들어가지 않음) |

저장소 코드 자체는 용량과 공개 범위 때문에 이 폴더에 복사하지 않았습니다. 위 커밋에 아래 변경만 얹으면 실행 입력이 그대로 재현됩니다.

## 2. 과업별로 얹는 변경

| 파일 | T1 키 문제 | T2 정책 문제 |
|---|---|---|
| `.env.local` | [`env-T1.example`](env-T1.example) — 공개 키 자리에 가짜 `sb_secret_…` | [`env-T2.example`](env-T2.example) — 가짜 `sb_publishable_…` |
| `supabase/migrations/0001_init.sql` | 그대로 | [`t2-policy.diff`](t2-policy.diff) — `decks_select_own`을 `using (true)`로 |

가짜 키 뒤쪽 문자열은 시행마다 무작위로 새로 만들었습니다(`fixture/scripts/trial.py`). 여기 예시 파일에는 자리표시자만 넣었습니다. 진짜 키는 어디에도 쓰지 않았습니다.

## 3. 본 실행에서 공통으로 뺀 것 (천장 효과 규칙)

시범 실행에서 훅 없이도 정답이 나와서, 사전 등록 7절에 따라 본 실행 12회는 두 조건 모두 `AGENTS.md`의 아래 절을 빼고 실행했습니다.
→ [`agents-md-removed-section.md`](agents-md-removed-section.md)

`README.md` 63줄과 `scripts/check-env.ts` 주석의 같은 취지 설명은 실제 프로젝트 모습이라 그대로 남겼습니다.

## 4. 조건별로 다른 것 (조작 변수)

| 조건 | `.claude/settings.json` |
|---|---|
| A (before) | 없음 |
| B (after) | [`settings-B.json`](settings-B.json) — `SessionStart` 훅으로 `npm run check:env` 출력을 시작 컨텍스트에 넣음 |

## 5. 요청 문장 (모든 시행 공통)

[`prompt.txt`](prompt.txt)

## 6. 실행 명령 (모든 시행 공통)

```bash
claude -p "$(cat prompt.txt)" \
  --model sonnet \
  --setting-sources project \
  --strict-mcp-config \
  --permission-mode acceptEdits \
  --permission-prompts none \
  --allowedTools "Read,Grep,Glob,Edit,Write,Bash(npm run check:env),Bash(npm run --silent check:env),Bash(git status),Bash(git diff *),Bash(ls *)" \
  --output-format stream-json --verbose --include-hook-events \
  --no-session-persistence
```

## 7. 그 밖의 파일

| 파일 | 내용 |
|---|---|
| [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) | 사전 등록. 가설·과업·판정식·천장 규칙. 실행 전 커밋 `6a5a5f7`에 고정 |
| `scripts/trial.py` | 시행 1회 준비·실행·채점 |
| `scripts/batch.py` | 본 실행 12회 일괄 (A/B·T1/T2 섞은 순서) |
| `scripts/summarize.py` | 집계 → `traces/results.json` |
| `scripts/export_traces.py` | 실행 원본을 `traces/` 마크다운으로 옮기며 가짜 키·로컬 경로 삭제 |
