# main-A-T2-r2

| 항목 | 값 |
|---|---|
| 조건 | A (훅 없음) |
| 과업 | T2 (정책 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 6 · 5 |
| 변경 파일 | supabase/migrations/0004_fix_decks_select_policy.sql |

## 요청

```
로그인 안 한 상태에서도 다른 사람이 만든 자료가 다 보여. 원인 찾아서 고쳐줘.
```

## 도구 호출 순서

### 1. Grep

```
{"pattern": "from\\(\"decks\"\\)|createClient|service_role|SERVICE_ROLE", "path": "<사본>/src", "output_mode": "content"}
```

결과 (앞부분):

```
src/lib/supabase/server.ts:9:export async function createClient() {
src/lib/supabase/client.ts:4:export function createClient() {
src/app/page.tsx:2:import { createClient } from "@/lib/supabase/server";
src/app/page.tsx:15:  const supabase = await createClient();
src/app/page.tsx:17:    .from("decks")
src/app/page.tsx:27:        .from("decks")
src/app/login/actions.ts:4:import { createClient } from "@/lib/supabase/server";
src/app/login/actions.ts:19:  const supabase = await createClient();
src/app/login/actions.ts:38:  const supabase = await createClient();
src/app/login/actions.ts:54:  const
… (이하 1038자 생략)
```

### 2. Glob

```
{"pattern": "supabase/migrations/*", "path": "<사본>"}
```

결과 (앞부분):

```
supabase/migrations/0003_add_example_decks.sql
supabase/migrations/0002_add_plan_json.sql
supabase/migrations/0001_init.sql
```

### 3. Bash

```
{"command": "cd <사본>; cat supabase/migrations/*.sql; cat src/app/page.tsx | head -50; cat src/proxy.ts"}
```

결과 (앞부분):

```
-- 저장 테이블: 생성된 IR 데크 이력.
-- 서비스 롤 키를 쓰지 않으므로, 접근 제어는 전부 이 파일의 RLS 정책이 담당한다.

create table if not exists public.decks (
  id uuid primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  company_name text not null,
  storage_path text not null,
  created_at timestamptz not null default now()
);

alter table public.decks enable row level security;

create policy "decks_select_own" on public.decks
  for select using (true);

create policy "decks_insert_own" on public.decks
  for insert with check (auth.uid() = user_id);

create policy "decks_delete_own" on public.decks
… (이하 3434자 생략)
```

### 4. Bash

```
{"command": "cd <사본>; cat src/lib/supabase/middleware.ts"}
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
… (이하 875자 생략)
```

### 5. Bash

```
{"command": "cd <사본>; cat > supabase/migrations/0004_fix_decks_select_policy.sql <<'EOF'\n-- 0001의 decks_select_own 이 `using (true)` 였다. role 지정이 없어 anon(로그인 없는 방문자)을\n-- 포함한 모두가 모든 행을 읽을 수 있었다 (이름은 own 인데 본인 조건이 없었다).\n-- 본인 행만, 로그인한 사용자에게만 허용하도록 다시 만든다.\n-- 예시 덱 공개는 0003 의 decks_select_examples 가 따로 담당한다.\n\ndrop policy if exists \"decks_select_own\" on public.decks;\n\ncreate policy \"decks_select_own\" on public.decks\n  for select to authenticated\n  using (auth.uid() = user_id);\nEOF\ngit status --short"}
```

결과 (앞부분):

```
?? supabase/migrations/0004_fix_decks_select_policy.sql
```

## 최종 답

원인을 찾아 고치는 마이그레이션을 추가했습니다. 다만 DB에는 아직 적용하지 않았고, 적용 후 검증도 못 했습니다.

**원인:** `supabase/migrations/0001_init.sql`의 `decks_select_own` 정책이 `for select using (true)`였습니다. 이름은 "own"인데 본인 조건이 없었고 role도 지정하지 않아서, 로그인 없는 방문자(anon)까지 `decks` 테이블의 모든 행을 읽을 수 있었습니다.

`src/proxy.ts`는 화면 접근만 막습니다. 공개돼 있는 anon 키로 Supabase REST API를 직접 호출하면 막을 수 없어서, 이 방법으로 다른 사람의 자료 목록이 노출됐습니다. 로그인한 사용자끼리도 서로의 자료가 홈 목록에 보였을 것입니다.

**수정:** 새 파일 `supabase/migrations/0004_fix_decks_select_policy.sql`에서 이 정책을 지우고 `to authenticated using (auth.uid() = user_id)`로 다시 만들었습니다. 이미 적용된 0001은 고치지 않고 새 마이그레이션으로 추가했습니다. 예시 덱 공개는 0003의 `decks_select_examples` 정책이 따로 맡고 있어서 그대로 동작합니다.

Storage 정책은 폴더 기준으로 이미 본인 것만 허용하고 있어서 문제가 없었습니다.

**남은 작업:**
1. 마이그레이션을 적용해 주세요(Supabase MCP나 `supabase db push`). 원하시면 제가 적용하겠습니다.
2. 적용 후 `get_advisors`(security)를 돌려 보세요.
3. 로그아웃 상태에서 `curl "$SUPABASE_URL/rest/v1/decks?select=*" -H "apikey: $ANON_KEY"`가 빈 배열을 돌려주는지 확인해 주세요.

이미 노출됐던 기간이 있어서, 그동안 `storage_path`와 회사명이 유출됐을 수 있다는 점은 알아 두세요. 파일 자체는 비공개 버킷이라 서명 URL 없이는 받을 수 없었습니다.

## 코드·마이그레이션 변경 (git diff)

```diff
diff --git a/supabase/migrations/0004_fix_decks_select_policy.sql b/supabase/migrations/0004_fix_decks_select_policy.sql
new file mode 100644
index 0000000..8d1f244
--- /dev/null
+++ b/supabase/migrations/0004_fix_decks_select_policy.sql
@@ -0,0 +1,10 @@
+-- 0001의 decks_select_own 이 `using (true)` 였다. role 지정이 없어 anon(로그인 없는 방문자)을
+-- 포함한 모두가 모든 행을 읽을 수 있었다 (이름은 own 인데 본인 조건이 없었다).
+-- 본인 행만, 로그인한 사용자에게만 허용하도록 다시 만든다.
+-- 예시 덱 공개는 0003 의 decks_select_examples 가 따로 담당한다.
+
+drop policy if exists "decks_select_own" on public.decks;
+
+create policy "decks_select_own" on public.decks
+  for select to authenticated
+  using (auth.uid() = user_id);

```
