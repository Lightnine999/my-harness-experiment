# main-A-T2-r1

| 항목 | 값 |
|---|---|
| 조건 | A (훅 없음) |
| 과업 | T2 (정책 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 10 · 9 |
| 변경 파일 | supabase/migrations/0001_init.sql, supabase/migrations/0004_fix_decks_select_policy.sql |

## 요청

```
로그인 안 한 상태에서도 다른 사람이 만든 자료가 다 보여. 원인 찾아서 고쳐줘.
```

## 도구 호출 순서

### 1. Grep

```
{"pattern": "from\\([\"']decks[\"']\\)|createClient|createServerClient|service_role|SERVICE_ROLE", "path": "src", "output_mode": "content"}
```

결과 (앞부분):

```
src/lib/supabase/server.ts:1:import { createServerClient } from "@supabase/ssr";
src/lib/supabase/server.ts:9:export async function createClient() {
src/lib/supabase/server.ts:12:  return createServerClient(
src/lib/supabase/client.ts:4:export function createClient() {
src/lib/supabase/middleware.ts:1:import { createServerClient } from "@supabase/ssr";
src/lib/supabase/middleware.ts:14:  const supabase = createServerClient(
src/app/page.tsx:2:import { createClient } from "@/lib/supabase/server";
src/app/page.tsx:15:  const supabase = await createClient();
src/app/page.tsx:17:    .from("decks")
… (이하 1336자 생략)
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

### 4. Read

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

### 5. Read

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

### 7. Read

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

### 8. Write

```
{"file_path": "<사본>/supabase/migrations/0004_fix_decks_select_policy.sql", "content": "-- 0001의 decks_select_own이 using (true)라 anon·타인에게도 모든 행이 읽혔다.\n-- 본인 행만, 로그인한 사용자에게만 열도록 다시 만든다.\n-- (예시 자료는 0003의 decks_select_examples가 따로 연다.)\n\ndrop policy if exists \"decks_select_own\" on public.decks;\n\ncreate policy \"decks_select_own\" on public.decks\n  for select to authenticated\n  using (auth.uid() = user_id);\n"}
```

결과 (앞부분):

```
File created successfully at: <사본>/supabase/migrations/0004_fix_decks_select_policy.sql (file state is current in your context — no need to Read it back)
```

### 9. Edit

```
{"replace_all": false, "file_path": "<사본>/supabase/migrations/0001_init.sql", "old_string": "  for select using (true);", "new_string": "  for select to authenticated using (auth.uid() = user_id);"}
```

결과 (앞부분):

```
The file <사본>/supabase/migrations/0001_init.sql has been updated successfully. (file state is current in your context — no need to Read it back)
```

## 최종 답

원인을 찾아 마이그레이션 파일은 고쳤습니다. 다만 DB에는 아직 적용하지 않았고, 동작 확인도 못 했습니다.

**원인:** `supabase/migrations/0001_init.sql`의 `decks_select_own` 정책이 `for select using (true)`였습니다. 조건이 없어서 anon(로그인 안 한 사용자)과 다른 사용자도 `decks` 테이블의 모든 행을 읽을 수 있었습니다. 서비스 롤 키를 쓰지 않고 접근 제어를 전부 RLS에 맡기는 구조라, 이 정책이 열려 있으면 화면과 상관없이 막히지 않습니다.

**수정:**
- 새 마이그레이션 `0004_fix_decks_select_policy.sql`을 추가했습니다. 기존 정책을 지우고 `to authenticated using (auth.uid() = user_id)`로 다시 만듭니다. 이미 적용된 DB는 이 파일로 고칩니다.
- `0001_init.sql`도 같은 조건으로 고쳤습니다. 새로 세팅하는 환경에 같은 문제가 생기지 않게 하려는 것입니다.

**남은 작업:**
1. 0004를 Supabase에 적용해 주세요. 이 환경에서는 DB에 직접 적용하지 않았습니다.
2. 적용 후 `get_advisors`(security)를 돌려 정책 누락이 없는지 확인해 주세요.
3. 로그아웃 상태에서 anon 키로 `decks`를 조회해 빈 결과가 나오는지 확인해 주세요.
4. 다른 계정으로 로그인해서도 타인의 자료가 안 보이는지 확인해 주세요.

**이미 노출된 가능성:**
- 정책이 열려 있던 동안 `company_name`, `storage_path` 같은 메타데이터는 외부에 보였을 수 있습니다.
- PPTX 파일은 Storage 정책이 본인 폴더로 제한돼 있어서 영향이 없습니다.
- 서명 URL은 본인 세션으로만 만들어집니다.

## 코드·마이그레이션 변경 (git diff)

```diff
diff --git a/supabase/migrations/0001_init.sql b/supabase/migrations/0001_init.sql
index 0466fab..7111053 100644
--- a/supabase/migrations/0001_init.sql
+++ b/supabase/migrations/0001_init.sql
@@ -12,7 +12,7 @@ create table if not exists public.decks (
 alter table public.decks enable row level security;
 
 create policy "decks_select_own" on public.decks
-  for select using (true);
+  for select to authenticated using (auth.uid() = user_id);
 
 create policy "decks_insert_own" on public.decks
   for insert with check (auth.uid() = user_id);
diff --git a/supabase/migrations/0004_fix_decks_select_policy.sql b/supabase/migrations/0004_fix_decks_select_policy.sql
new file mode 100644
index 0000000..cd0cf92
--- /dev/null
+++ b/supabase/migrations/0004_fix_decks_select_policy.sql
@@ -0,0 +1,9 @@
+-- 0001의 decks_select_own이 using (true)라 anon·타인에게도 모든 행이 읽혔다.
+-- 본인 행만, 로그인한 사용자에게만 열도록 다시 만든다.
+-- (예시 자료는 0003의 decks_select_examples가 따로 연다.)
+
+drop policy if exists "decks_select_own" on public.decks;
+
+create policy "decks_select_own" on public.decks
+  for select to authenticated
+  using (auth.uid() = user_id);

```
