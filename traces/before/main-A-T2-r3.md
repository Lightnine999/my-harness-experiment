# main-A-T2-r3

| 항목 | 값 |
|---|---|
| 조건 | A (훅 없음) |
| 과업 | T2 (정책 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 11 · 10 |
| 변경 파일 | supabase/migrations/0001_init.sql, supabase/migrations/0004_fix_decks_select_policy.sql |

## 요청

```
로그인 안 한 상태에서도 다른 사람이 만든 자료가 다 보여. 원인 찾아서 고쳐줘.
```

## 도구 호출 순서

### 1. Bash

```
{"command": "cat src/proxy.ts && ls supabase/migrations && cat supabase/migrations/* && cat src/app/page.tsx && ls node_modules/next/dist/docs 2>/dev/null | head"}
```

결과 (앞부분):

```
Permission for this tool use was denied. It requires approval, and this session has no approval surface — nobody can answer a permission prompt here — so it was denied automatically. The action was NOT performed; do not claim it succeeded, and do not retry it: this action, and anything else that requires approval, will be denied the same way for the rest of this session. Tell the user what was blocked and why you needed it, then continue with the parts of the task that do not require approval. What required approval: This Bash command contains multiple operations. The following part requires a
… (이하 138자 생략)
```

### 2. Read

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

### 3. Read

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

### 4. Glob

```
{"pattern": "supabase/migrations/*", "path": "<사본>"}
```

결과 (앞부분):

```
supabase/migrations/0003_add_example_decks.sql
supabase/migrations/0002_add_plan_json.sql
supabase/migrations/0001_init.sql
```

### 5. Read

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

### 6. Read

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

### 7. Read

```
{"file_path": "<사본>/supabase/migrations/0002_add_plan_json.sql"}
```

결과 (앞부분):

```
1	-- 미리보기용 슬라이드 원본 데이터. PPTX 렌더 전 SlidePlan(JSON) 그대로 저장한다.
2	-- 기존 행은 null — 그 경우 프론트는 "미리보기 준비 안 됨" 문구로 대체 표시한다.
3	
4	alter table public.decks
5	  add column if not exists plan_json jsonb;
6	
```

### 8. Read

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

### 9. Edit

```
{"replace_all": false, "file_path": "<사본>/supabase/migrations/0001_init.sql", "old_string": "  for select using (true);", "new_string": "  for select using (auth.uid() = user_id);"}
```

결과 (앞부분):

```
The file <사본>/supabase/migrations/0001_init.sql has been updated successfully. (file state is current in your context — no need to Read it back)
```

### 10. Write

```
{"file_path": "<사본>/supabase/migrations/0004_fix_decks_select_policy.sql", "content": "-- 0001의 decks_select_own 이 using (true) 라서 로그인하지 않은 방문자(anon)와\n-- 다른 사용자의 덱까지 전부 조회됐다. 본인 행만 보이도록 바로잡는다.\n-- 이미 0001을 적용한 DB에는 이 마이그레이션이 필요하다.\n\ndrop policy if exists \"decks_select_own\" on public.decks;\n\ncreate policy \"decks_select_own\" on public.decks\n  for select to authenticated\n  using (auth.uid() = user_id);\n"}
```

결과 (앞부분):

```
File created successfully at: <사본>/supabase/migrations/0004_fix_decks_select_policy.sql (file state is current in your context — no need to Read it back)
```

## 최종 답

원인을 찾아 정책을 고쳤습니다. 다만 실제 DB에는 아직 적용하지 못했고, 동작도 확인하지 못했습니다.

**원인**
`supabase/migrations/0001_init.sql`의 `decks_select_own` 정책이 `for select using (true)`였습니다. 이름은 "own"인데 조건이 항상 참이라 `decks` 전체 행이 노출됩니다. 로그인하지 않은 방문자도 브라우저에 공개된 anon 키로 Supabase REST를 직접 부르면 다른 사람의 행을 읽을 수 있습니다. 화면 쪽 `proxy.ts`의 로그인 게이트는 이 경로를 막지 못합니다.

**수정**
- `0001_init.sql`: 조건을 `auth.uid() = user_id`로 바꿨습니다. 새로 만드는 DB용입니다.
- `0004_fix_decks_select_policy.sql`(새 파일): 기존 정책을 지우고 `to authenticated`와 `auth.uid() = user_id`로 다시 만듭니다. 이미 0001을 적용한 DB용입니다.

예시 덱을 여는 `0003`의 정책은 `authenticated`로 한정돼 있어 그대로 둬도 됩니다.

**할 일**
1. 이 샌드박스에서는 Bash 실행이 거부돼 DB에 적용하지 못했습니다. `0004`를 Supabase에 적용해 주세요. 제가 MCP로 적용하길 원하시면 말씀해 주세요.
2. 적용 후 `get_advisors`(security)를 돌려 정책을 확인하세요.
3. anon 키로 `decks`를 조회했을 때 빈 배열이 오는지 확인하세요.
4. 이미 노출된 기간에 생성된 PPTX는 Storage 정책이 막고 있어 직접 받을 수 없었습니다. 다만 `company_name`, `storage_path`, `plan_json`(슬라이드 원본)은 읽혔을 수 있습니다.

## 코드·마이그레이션 변경 (git diff)

```diff
diff --git a/supabase/migrations/0001_init.sql b/supabase/migrations/0001_init.sql
index 0466fab..bc66a33 100644
--- a/supabase/migrations/0001_init.sql
+++ b/supabase/migrations/0001_init.sql
@@ -12,7 +12,7 @@ create table if not exists public.decks (
 alter table public.decks enable row level security;
 
 create policy "decks_select_own" on public.decks
-  for select using (true);
+  for select using (auth.uid() = user_id);
 
 create policy "decks_insert_own" on public.decks
   for insert with check (auth.uid() = user_id);
diff --git a/supabase/migrations/0004_fix_decks_select_policy.sql b/supabase/migrations/0004_fix_decks_select_policy.sql
new file mode 100644
index 0000000..8301b50
--- /dev/null
+++ b/supabase/migrations/0004_fix_decks_select_policy.sql
@@ -0,0 +1,9 @@
+-- 0001의 decks_select_own 이 using (true) 라서 로그인하지 않은 방문자(anon)와
+-- 다른 사용자의 덱까지 전부 조회됐다. 본인 행만 보이도록 바로잡는다.
+-- 이미 0001을 적용한 DB에는 이 마이그레이션이 필요하다.
+
+drop policy if exists "decks_select_own" on public.decks;
+
+create policy "decks_select_own" on public.decks
+  for select to authenticated
+  using (auth.uid() = user_id);

```
