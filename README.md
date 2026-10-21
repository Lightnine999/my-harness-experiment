# my-harness-experiment

기준 도구: Claude Code CLI · 모델 `claude-sonnet-5-5` · 다룬 하네스 기능: **컨텍스트 관리** (`SessionStart` 훅)
(모두의연구소 AI 에이전트 2기, 「에이전트 하네스 톺아보기」 과제 「도구의 불편을 개선 가설로 바꿔 실험하기」)

전체 보고서는 [experiment-01.md](experiment-01.md)에 있다. 판정식은 실행 전에 [fixture/PRE-REGISTRATION.md](fixture/PRE-REGISTRATION.md)로 커밋했다(`6a5a5f7`).

## 불편

직접 만든 IR 자료 생성 서비스(Next.js + Supabase)에서, 로그인하지 않은 사용자에게 남의 자료가 다 보였다.
Claude Code는 "RLS 정책이 빠졌다"고 단정했지만 **오진**이었다. 진짜 원인은 공개 키 자리에 들어간 비밀 키(`sb_secret_`)였다.
그 뒤 키 종류를 판정하는 `npm run check:env`를 만들었다. 그런데 이 검사는 누군가 실행해야만 돌아가고, 효과를 재 본 적도 없었다.

## 가설

> 같은 증상을 받았을 때, 하네스가 세션 시작 시 키 검사 결과를 에이전트 컨텍스트에 넣으면(`SessionStart` 훅) 원인을 맞게 짚는다.
> 원인이 정책일 때는 여전히 정책을 짚는다.

## 실험 설계

| 구분 | 내용 |
|---|---|
| 고정 | Claude Code CLI `claude -p`, `claude-sonnet-5-5`, 저장소 사본(커밋 `4552c90`, 시행마다 새로 풀어 씀), 같은 요청 문장, 같은 허용 도구, `--setting-sources project --strict-mcp-config` |
| 조작 (하나) | `SessionStart` 훅 — A: 없음 / B: `check:env` 출력을 시작 컨텍스트에 넣음 |
| 과업 | T1 키 문제(가짜 `sb_secret_` 키) · T2 정책 문제(`using (true)` 정책). **증상과 요청 문장은 같고 원인만 반대** |
| 측정 | 첫 원인이 맞았는가 + 반대쪽 파일 수정, 가짜 키 유출, 턴, 도구 호출, 토큰 |
| 반론과 통제 | "훅이 무조건 키 탓을 하게 만든다" → T2 짝 / "검사 도구가 있느냐의 차이" → A에도 `check:env` 실행 허용 / "문서에 이미 교훈이 있다" → 천장 효과 규칙으로 두 조건 모두 해당 절 제거 |
| 반복 | 2 조건 × 2 과업 × 3회 = 12회, 순서 교차 |
| 사전 판정식 | B에서 T1·T2 6회 모두 맞는 진단, 유출 0이면 지지. 그 외 기각 |

## 결과와 판정

| 조건 | T1 키 문제 | T2 정책 문제 | 반대쪽 수정 | 유출 | T1 평균 토큰 |
|---|---|---|---|---|---|
| A 훅 없음 (before) | **2 / 3** | 3 / 3 | 0 | 0 | 178,917 |
| B 훅 있음 (after) | **3 / 3** | 3 / 3 | 0 | 0 | 108,883 |

**판정: 지지.** A가 틀린 1회는 `check:env`를 한 번도 실행하지 않은 실행이었다. 맞힌 2회는 둘 다 스스로 검사를 떠올렸다.
훅이 바꾼 것은 **"에이전트가 검사를 떠올리느냐"라는 우연**이었다. B는 정책 문제(T2)에서도 키 탓을 하지 않았다.

**한계** — 조건당 3회, 차이는 1회다. 천장 효과 때문에 AGENTS.md 교훈 절을 빼고 돌렸다(그 절이 있으면 A도 맞혔다). 가짜 환경이라 실제 DB는 조회할 수 없었다. 전역 CLAUDE.md·자동 메모리가 완전히 빠졌는지는 확인하지 못했다.

## 다시 검토할 조건

- 반복을 10회 이상으로 늘렸는데 A·T1 정답률이 B와 같아질 때
- 모델이나 Claude Code 버전을 바꿨는데 훅 없이도 매번 `check:env`를 먼저 실행할 때
- 전역 CLAUDE.md·자동 메모리를 확실히 끈 상태에서 결과가 달라질 때
- 다음 실험: AGENTS.md 교훈 절 × 훅 4조건으로, 메모리 문장과 시작 컨텍스트 중 어느 쪽이 오진을 막는지 나눈다([experiment-01.md 7절](experiment-01.md#7-다음-실험-계획과-재검토-조건))

## 폴더 구성

```
my-harness-experiment/
├── README.md          # 가설, 실험 설계, 결과, 다시 검토할 조건 요약
├── experiment-01.md   # 실험 보고서 (불편·가설, 근거, 설계, 실행 기록, 결과, 돌아보기, 다음 계획)
├── traces/            # 수정 전(before = A)·후(after = B)의 실행 기록, 시범 실행, 집계·판정
└── fixture/           # 고정한 작업 입력 원본, 사전 등록, 실행 스크립트
```

실행 기록 원본(stream-json)에는 가짜 키와 로컬 경로가 들어 있어서, 그것을 지운 정리본(`fixture/scripts/export_traces.py`)만 올렸다.

## 다시 돌리기

```bash
git -C ~/Web_Development worktree add --detach ~/harness-exp/ir-base 4552c90
cd fixture/scripts
python3 batch.py && python3 summarize.py --final && python3 export_traces.py
```

필요한 것: 로그인된 Claude Code, 대상 저장소(`Web_Development`)와 `node_modules`. 대상 저장소 코드는 이 저장소에 넣지 않았다. 결과는 모델 상태에 따라 달라질 수 있다.
