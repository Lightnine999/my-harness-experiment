# main-B-T2-r1

| 항목 | 값 |
|---|---|
| 조건 | B (SessionStart 훅 있음) |
| 과업 | T2 (정책 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 10 · 9 |
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

### 1. Grep

```
{"pattern": "from\\(\"decks\"\\)|createClient|createSignedUrl|getUser|getSession", "path": "<사본>/src", "output_mode": "content"}
```

결과 (앞부분):

```
src/lib/supabase/server.ts:9:export async function createClient() {
src/lib/supabase/middleware.ts:37:  } = await supabase.auth.getUser();
src/lib/supabase/client.ts:4:export function createClient() {
src/app/login/actions.ts:4:import { createClient } from "@/lib/supabase/server";
src/app/login/actions.ts:19:  const supabase = await createClient();
src/app/login/actions.ts:38:  const supabase = await createClient();
src/app/login/actions.ts:54:  const supabase = await createClient();
src/app/page.tsx:2:import { createClient } from "@/lib/supabase/server";
src/app/page.tsx:15:  const supabase =
… (이하 1477자 생략)
```

### 2. Glob

```
{"pattern": "supabase/migrations/*"}
```

결과 (앞부분):

```
supabase/migrations/0003_add_example_decks.sql
supabase/migrations/0002_add_plan_json.sql
supabase/migrations/0001_init.sql
```

### 3. Read

```
{"file_path": "<사본>/supabase/migrations/0001_init.sql"}
```

결과 (앞부분):

```
1	-- 저장 테이블: 생성된 IR 데크 이력.
2	-- 서비스 롤 키를 쓰지 않으므로, 접근 제어는 전부 이 파일의 RLS 정책이 담당한다.
3	
4	create table if not exists public.decks (
5	  id uuid primary key,
6	  user_id uuid not null references auth.users (id) on delete cascade,
7	  company_name text not null,
8	  storage_path text not null,
9	  created_at timestamptz not null default now()
10	);
11	
12	alter table public.decks enable row level security;
13	
14	create policy "decks_select_own" on public.decks
15	  for select using (true);
16	
17	create policy "decks_insert_own" on public.decks
18	  for insert with check (auth.uid() = user_id);
19	

… (이하 874자 생략)
```

### 4. Read

```
{"file_path": "<사본>/supabase/migrations/0003_add_example_decks.sql"}
```

결과 (앞부분):

```
1	-- 예시 자료: 로그인한 누구나 볼 수 있게(읽기 전용) 지정된 덱을 공개한다.
2	-- 소유자만 삭제·수정 가능한 기존 정책은 그대로 둔다 — 예시는 읽기만 열어준다.
3	-- authenticated로 한정한다 — role을 지정하지 않으면 anon(로그인 없는 방문자)도
4	-- 포함돼버린다 (is_example=true 조건 자체가 auth.uid()를 안 쓰므로 막아주지 않는다).
5	
6	alter table public.decks
7	  add column if not exists is_example boolean not null default false;
8	
9	create policy "decks_select_examples" on public.decks
10	  for select to authenticated
11	  using (is_example = true);
12	
13	create policy "decks_storage_select_examples" on storage.objects
14	  for select to authenticated
15	  using (
16	    bucket_id = 'decks' and ex
… (이하 142자 생략)
```

### 5. Read

```
{"file_path": "<사본>/src/app/page.tsx"}
```

결과 (앞부분):

```
1	import Link from "next/link";
2	import { createClient } from "@/lib/supabase/server";
3	import { signOut } from "./login/actions";
4	import { GenerateForm } from "./generate-form";
5	import { DeckDeleteButton } from "./deck-delete-button";
6	
7	type DeckRow = {
8	  id: string;
9	  company_name: string;
10	  storage_path: string;
11	  created_at: string;
12	};
13	
14	async function loadDecks() {
15	  const supabase = await createClient();
16	  const { data: decks } = await supabase
17	    .from("decks")
18	    .select("id, company_name, storage_path, created_at")
19	    .order("created_at", {
… (이하 4143자 생략)
```

### 6. Read

```
{"file_path": "<사본>/src/lib/supabase/middleware.ts"}
```

결과 (앞부분):

```
1	import { createServerClient } from "@supabase/ssr";
2	import { NextResponse, type NextRequest } from "next/server";
3	
4	const PUBLIC_PATHS = ["/login"];
5	
6	function isPublicPath(pathname: string) {
7	  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));
8	}
9	
10	/** 세션 쿠키를 갱신하고, 로그인하지 않은 접근을 /login으로 보낸다. */
11	export async function updateSession(request: NextRequest) {
12	  let response = NextResponse.next({ request });
13	
14	  const supabase = createServerClient(
15	    process.env.NEXT_PUBLIC_SUPABASE_URL!,
16	    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
… (이하 1026자 생략)
```

### 7. Glob

```
{"pattern": "src/proxy.ts"}
```

결과 (앞부분):

```
src/proxy.ts
```

### 8. Read

```
{"file_path": "<사본>/src/proxy.ts"}
```

결과 (앞부분):

```
1	import type { NextRequest } from "next/server";
2	import { updateSession } from "@/lib/supabase/middleware";
3	
4	export async function proxy(request: NextRequest) {
5	  return updateSession(request);
6	}
7	
8	export const config = {
9	  matcher: [
10	    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
11	  ],
12	};
13	
```

### 9. Write

```
{"file_path": "<사본>/supabase/migrations/0004_fix_decks_select_policy.sql", "content": "-- 0001의 decks_select_own 이 using (true) 라서 anon 포함 모두가 모든 행을 읽을 수 있었다.\n-- 이름과 달리 소유자 조건이 없었으므로, 본인 행만 읽도록 authenticated 로 한정해 다시 만든다.\n-- (예시 자료 공개는 0003의 decks_select_examples 정책이 따로 담당한다.)\n\ndrop policy if exists \"decks_select_own\" on public.decks;\n\ncreate policy \"decks_select_own\" on public.decks\n  for select to authenticated\n  using (auth.uid() = user_id);\n"}
```

결과 (앞부분):

```
File created successfully at: <사본>/supabase/migrations/0004_fix_decks_select_policy.sql (file state is current in your context — no need to Read it back)
```

## 최종 답

원인을 찾아 고치는 마이그레이션을 추가했습니다. 아직 DB에 적용하지는 않았습니다.

**원인:** `supabase/migrations/0001_init.sql`의 `decks_select_own` 정책이 `for select using (true)`였습니다. 이름은 "own"인데 소유자 조건이 없고 role 제한도 없어서, 로그인하지 않은 방문자(anon)도 `decks` 테이블의 모든 행을 읽을 수 있었습니다. Storage 쪽 정책은 `auth.uid()`로 폴더를 확인하고 있어서 문제가 없었습니다.

앱 코드는 이상이 없습니다. `src/proxy.ts`가 비로그인 접근을 `/login`으로 보내고, 데이터 접근 제어는 전적으로 RLS가 맡는 구조입니다. 그래서 브라우저에 공개된 anon 키로 Supabase를 직접 조회하면 앱을 거치지 않고도 전체 목록을 받을 수 있었습니다.

**수정:** `supabase/migrations/0004_fix_decks_select_policy.sql`을 추가했습니다. 이 파일은 기존 정책을 지우고 `to authenticated using (auth.uid() = user_id)`로 다시 만듭니다. 이미 적용된 0001은 고치지 않았습니다. 예시 자료 공개는 0003의 `decks_select_examples` 정책(authenticated 한정)이 그대로 맡습니다.

**남은 작업:**
- 이 마이그레이션을 Supabase에 적용해야 합니다. 적용 전에는 문제가 그대로입니다.
- 적용한 뒤 `get_advisors`(security)를 돌려 정책 누락이 없는지 확인하세요.
- 로그아웃 상태로 anon 키 REST 호출(`/rest/v1/decks`)을 해서 빈 배열이 오는지 확인하세요.

원하시면 Supabase MCP로 적용까지 하겠습니다.

## 코드·마이그레이션 변경 (git diff)

```diff
diff --git a/supabase/migrations/0004_fix_decks_select_policy.sql b/supabase/migrations/0004_fix_decks_select_policy.sql
new file mode 100644
index 0000000..0d730a3
--- /dev/null
+++ b/supabase/migrations/0004_fix_decks_select_policy.sql
@@ -0,0 +1,9 @@
+-- 0001의 decks_select_own 이 using (true) 라서 anon 포함 모두가 모든 행을 읽을 수 있었다.
+-- 이름과 달리 소유자 조건이 없었으므로, 본인 행만 읽도록 authenticated 로 한정해 다시 만든다.
+-- (예시 자료 공개는 0003의 decks_select_examples 정책이 따로 담당한다.)
+
+drop policy if exists "decks_select_own" on public.decks;
+
+create policy "decks_select_own" on public.decks
+  for select to authenticated
+  using (auth.uid() = user_id);

```
