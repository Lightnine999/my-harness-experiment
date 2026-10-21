# 본 실행에서 AGENTS.md에서 뺀 절 (원문 34~49줄)

천장 효과 규칙(사전 등록 7절)에 따라 본 실행 12회는 두 조건 모두 아래 절을 뺀 상태로 실행했습니다.
다음 `### ` 제목 직전까지를 통째로 뺐습니다 (`fixture/scripts/trial.py`의 `strip_key_section`).

---

### `NEXT_PUBLIC_` 에 비밀 값을 넣지 마라

이 접두사가 붙은 값은 빌드 시 **브라우저 번들에 그대로 인라인된다.**
2026-09-08에 `NEXT_PUBLIC_SUPABASE_ANON_KEY` 자리에 Supabase `sb_secret_` 키가 들어가
있었다. 이 키는 service role급이라 RLS를 설계상 우회하므로, 정책이 다 걸려 있는데도
익명 요청으로 남의 자료가 전부 조회되고 PPTX가 다운로드됐다.

`sb_publishable_`(공개용)과 `sb_secret_`(비밀)은 길이가 46자 대 41자로 비슷해 눈으로
구별되지 않는다. 눈으로 보지 말고 검사해라.

```bash
npm run check:env      # 키 종류를 판정한다. 값은 출력하지 않는다
```

**RLS가 안 듣는 것처럼 보이면 정책을 고치기 전에 키 종류를 먼저 의심해라.** 정책 실제
상태는 Supabase MCP(`get_advisors`, `execute_sql`)로 확인한다. 증상만 보고 단정하지 마라.
