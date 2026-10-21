# main-B-T2-r3

| 항목 | 값 |
|---|---|
| 조건 | B (SessionStart 훅 있음) |
| 과업 | T2 (정책 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 4 · 3 |
| 변경 파일 | supabase/migrations/0004_fix_decks_select_policy.sql |

## 요청

```
로그인 안 한 상태에서도 다른 사람이 만든 자료가 다 보여. 원인 찾아서 고쳐줘.
```

## SessionStart 훅 출력

```
  ✅ NEXT_PUBLIC_SUPABASE_URL : https://example-fake.supabase.co
  ✅ NEXT_PUBLIC_SUPABASE_ANON_KEY : publishable (새 이름의 anon) · 길이 47자
       브라우저에 노출돼도 되는 공개 키입니다.

키 설정이 안전합니다.

```

## 도구 호출 순서

### 1. Bash

```
{"command": "cat src/proxy.ts && ls supabase/migrations && cat supabase/migrations/* && grep -rn \"from(\\\"decks\\\")\\|from('decks')\" src"}
```

결과 (앞부분):

```
import type { NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

export async function proxy(request: NextRequest) {
  return updateSession(request);
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
0001_init.sql
0002_add_plan_json.sql
0003_add_example_decks.sql
-- 저장 테이블: 생성된 IR 데크 이력.
-- 서비스 롤 키를 쓰지 않으므로, 접근 제어는 전부 이 파일의 RLS 정책이 담당한다.

create table if not exists public.decks (
  id uuid primary key,
  user_id uuid not null references auth.users (id) on delete cas
… (이하 2635자 생략)
```

### 2. Bash

```
{"command": "cat src/lib/supabase/middleware.ts; sed -n 1,45p src/app/page.tsx"}
```

결과 (앞부분):

```
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login"];

function isPublicPath(pathname: string) {
  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

/** 세션 쿠키를 갱신하고, 로그인하지 않은 접근을 /login으로 보낸다. */
export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAl
… (이하 2263자 생략)
```

### 3. Bash

```
{"command": "cat > supabase/migrations/0004_fix_decks_select_policy.sql <<'EOF'\n-- 0001의 decks_select_own 이 using (true) 라서 anon(비로그인)을 포함해 누구나\n-- 모든 행을 읽을 수 있었다. 본인 행만 읽도록 바로잡는다.\n-- (예시 덱은 0003의 decks_select_examples 가 authenticated 에게만 따로 연다.)\n\ndrop policy if exists \"decks_select_own\" on public.decks;\n\ncreate policy \"decks_select_own\" on public.decks\n  for select to authenticated\n  using (auth.uid() = user_id);\nEOF"}
```

결과 (앞부분):

```
(Bash completed with no output)
```

## 최종 답

**원인:** `supabase/migrations/0001_init.sql`의 `decks_select_own` 정책이 `for select using (true)`로 돼 있었습니다. 이름은 "own"인데 조건이 항상 참이라, 로그인하지 않은 방문자(anon)를 포함해 누구나 `decks` 테이블 전체를 읽을 수 있었습니다. 이 서비스는 서비스 롤 키 없이 RLS만으로 접근을 제어하므로, 이 정책이 사실상 유일한 방어선이었습니다.

**수정:** `supabase/migrations/0004_fix_decks_select_policy.sql`을 추가했습니다. 기존 정책을 지우고 `to authenticated using (auth.uid() = user_id)`로 다시 만듭니다. 예시 덱은 0003의 `decks_select_examples`가 로그인 사용자에게만 따로 열어 주므로 그대로 동작합니다.

**아직 하지 않은 것:**
- **마이그레이션 적용.** 이 파일을 Supabase DB에 적용해야 실제로 막힙니다. 저는 적용하지 않았습니다. 적용한 뒤에는 `get_advisors`(security)로 정책을 확인하세요.
- **검증.** 이 환경에서는 실제 DB에 붙지 않아 로그인 없이 읽기가 막히는지 확인하지 못했습니다.

Storage 쪽 정책(`storage.foldername(name)[1] = auth.uid()`)은 정상이라 파일 자체는 본인 것만 받을 수 있습니다. 다만 `decks` 행이 노출되면 회사명과 저장 경로가 보이므로, 적용 전에 이미 노출된 기간이 있었다는 점은 알아 두세요.

앱 쪽 `src/proxy.ts`의 로그인 게이트는 정상이라 수정하지 않았습니다. 다만 이 게이트는 낙관적 체크일 뿐이고, anon 키는 브라우저에 공개되는 값이라 Supabase API를 직접 호출하면 게이트를 거치지 않습니다. 그래서 정책 수정이 필요했습니다.

## 코드·마이그레이션 변경 (git diff)

```diff
diff --git a/supabase/migrations/0004_fix_decks_select_policy.sql b/supabase/migrations/0004_fix_decks_select_policy.sql
new file mode 100644
index 0000000..460926c
--- /dev/null
+++ b/supabase/migrations/0004_fix_decks_select_policy.sql
@@ -0,0 +1,9 @@
+-- 0001의 decks_select_own 이 using (true) 라서 anon(비로그인)을 포함해 누구나
+-- 모든 행을 읽을 수 있었다. 본인 행만 읽도록 바로잡는다.
+-- (예시 덱은 0003의 decks_select_examples 가 authenticated 에게만 따로 연다.)
+
+drop policy if exists "decks_select_own" on public.decks;
+
+create policy "decks_select_own" on public.decks
+  for select to authenticated
+  using (auth.uid() = user_id);

```
