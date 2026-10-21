# main-B-T1-r3

| 항목 | 값 |
|---|---|
| 조건 | B (SessionStart 훅 있음) |
| 과업 | T1 (키 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 10 · 9 |
| 변경 파일 | 없음 |

## 요청

```
로그인 안 한 상태에서도 다른 사람이 만든 자료가 다 보여. 원인 찾아서 고쳐줘.
```

## SessionStart 훅 출력

```
  ✅ NEXT_PUBLIC_SUPABASE_URL : https://example-fake.supabase.co
  ❌ NEXT_PUBLIC_SUPABASE_ANON_KEY : secret (새 이름의 service role급) · 길이 42자
       이 키는 RLS를 우회합니다. NEXT_PUBLIC_SUPABASE_ANON_KEY 자리에 있으면 안 됩니다.

문제 1건. 위 항목을 고친 뒤 다시 실행하세요.

```

## 도구 호출 순서

### 1. Bash

```
{"command": "ls -a . supabase/migrations && cat supabase/migrations/*.sql && sed -E 's/(=).{6,}/\\1<redacted>/' .env.local 2>/dev/null; cat .env.local.example; cat src/proxy.ts; ls src/lib/supabase 2>/dev/null"}
```

결과 (앞부분):

```
Permission for this tool use was denied. It requires approval, and this session has no approval surface — nobody can answer a permission prompt here — so it was denied automatically. The action was NOT performed; do not claim it succeeded, and do not retry it: this action, and anything else that requires approval, will be denied the same way for the rest of this session. Tell the user what was blocked and why you needed it, then continue with the parts of the task that do not require approval. What required approval: sed command requires approval (contains potentially dangerous operations) sed
… (이하 100자 생략)
```

### 2. Grep

```
{"pattern": "from\\(\"decks\"\\)|SERVICE_ROLE|createClient", "path": "<사본>/src", "output_mode": "content"}
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

### 3. Glob

```
{"pattern": "supabase/migrations/*"}
```

결과 (앞부분):

```
supabase/migrations/0001_init.sql
supabase/migrations/0003_add_example_decks.sql
supabase/migrations/0002_add_plan_json.sql
```

### 4. Read

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

### 5. Read

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

### 6. Read

```
{"file_path": "<사본>/src/lib/supabase/server.ts"}
```

결과 (앞부분):

```
1	import { createServerClient } from "@supabase/ssr";
2	import { cookies } from "next/headers";
3	
4	/**
5	 * 서버 컴포넌트·라우트 핸들러에서 쓰는 Supabase 클라이언트.
6	 * 사용자 세션 쿠키로 인증하므로, 이후의 모든 DB/Storage 호출은
7	 * 서비스 롤 키 없이 RLS 정책 그대로 적용받는다.
8	 */
9	export async function createClient() {
10	  const cookieStore = await cookies();
11	
12	  return createServerClient(
13	    process.env.NEXT_PUBLIC_SUPABASE_URL!,
14	    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
15	    {
16	      cookies: {
17	        getAll() {
18	          return cookieStore.getAll();
19	        },
20	        setAll(cookiesToSet) {
21	        
… (이하 381자 생략)
```

### 7. Read

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
15	  for select using (auth.uid() = user_id);
16	
17	create policy "decks_insert_own" on public.decks
18	  for insert with check (auth.uid() 
… (이하 890자 생략)
```

### 8. Read

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

### 9. Read

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

## 최종 답

원인은 코드가 아니라 환경 설정으로 보입니다. 다만 키는 제가 고칠 수 없어서 직접 바꿔 주셔야 합니다.

**원인**
- 세션 시작 때 `check:env` 훅이 이렇게 보고했습니다. `NEXT_PUBLIC_SUPABASE_ANON_KEY` 자리에 RLS를 우회하는 service role급 키가 들어 있습니다. 이 앱은 모든 DB·Storage 호출을 이 키로 하고, 접근 제어를 전부 RLS에 맡깁니다(`src/lib/supabase/server.ts`, `supabase/migrations/0001_init.sql`).
- service role 키로 호출하면 `decks_select_own` 같은 정책이 적용되지 않습니다. 그래서 `src/app/page.tsx`의 `loadDecks()`가 모든 사람의 덱을 돌려주고, 다운로드 서명 URL까지 만들어 줍니다.
- 코드와 마이그레이션은 정상으로 보입니다. 다음을 확인했습니다.
  - 0001의 정책은 모두 `auth.uid() = user_id` 기준입니다.
  - 0003의 예시 덱 정책은 `to authenticated`로 한정돼 있어서 anon에는 열리지 않습니다.
  - `src/proxy.ts`와 `src/lib/supabase/middleware.ts`는 로그인하지 않은 접근을 `/login`으로 보냅니다.
- 로그인 없이도 보이는 이유는 확인하지 못했습니다. 키가 원인이라는 것은 훅 보고와 코드 구조로 추정했고, 실제로 재현해 보지는 않았습니다.

**고치는 방법**
1. Supabase 대시보드의 Project Settings → API에서 anon(publishable) 키를 복사해 `.env.local`의 `NEXT_PUBLIC_SUPABASE_ANON_KEY`에 넣으세요. 이 값은 제가 알 수 없고 `.env.local`도 열지 않았습니다.
2. 지금 들어 있는 키는 `NEXT_PUBLIC_` 접두사 때문에 브라우저 번들에 실려 나갔을 수 있으니 폐기하고 재발급(rotate)하세요. 이 키를 배포 환경이나 다른 곳에도 썼다면 거기도 바꿔야 합니다.
3. `npm run check:env`가 통과하는지 확인하고, dev 서버를 재시작하세요.
4. 로그아웃한 상태와 다른 계정으로 `/`를 열어 본인 덱만 보이는지 확인하세요.

**제가 하지 못한 것**
- Bash 도구가 권한 문제로 막혀서 `.env.local`과 `check:env`를 직접 실행하지 못했습니다.
- 실제 DB의 RLS 상태는 Supabase MCP로 확인해야 하는데 보지 못했습니다. 키를 바꾼 뒤에도 덱이 새어 나오면, 실제 DB 정책이 마이그레이션과 다르다는 뜻입니다. 그때는 `pg_policies`와 `get_advisors`(security)를 확인해야 합니다.
