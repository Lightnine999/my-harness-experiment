# main-B-T1-r1

| 항목 | 값 |
|---|---|
| 조건 | B (SessionStart 훅 있음) |
| 과업 | T1 (키 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 7 · 6 |
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
{"command": "ls -a . src src/lib src/lib/* supabase/migrations 2>/dev/null | head -80; cat src/proxy.ts; cat supabase/migrations/*.sql; cat .env.local.example; sed 's/=.*/=<hidden>/' .env.local 2>/dev/null"}
```

결과 (앞부분):

```
src/lib/pdf.ts

.:
.
..
.claude
.env.local
.env.local.example
.git
.gitignore
AGENTS.md
CLAUDE.md
README.md
Review.md
backend
design
docs
eslint.config.mjs
next.config.ts
node_modules
openapi
package-lock.json
package.json
postcss.config.mjs
public
scripts
src
supabase
tsconfig.json

src:
.
..
api
app
lib
mocks
proxy.ts

src/lib:
.
..
deck
messages
pdf.ts
supabase

src/lib/deck:
.
..
blocks
frame.ts
generate-client.ts
generate.ts
render.ts
schema.ts
theme.ts

src/lib/messages:
.
..
errors.ts

src/lib/supabase:
.
..
client.ts
middleware.ts
server.ts

supabase/migrations:
.
..
0001_init.sql
0002
… (이하 3771자 생략)
```

### 2. Grep

```
{"pattern": "from\\(\"decks\"\\)|createClient|SERVICE_ROLE|ANON_KEY", "path": "<사본>/src", "output_mode": "content"}
```

결과 (앞부분):

```
src/lib/supabase/server.ts:9:export async function createClient() {
src/lib/supabase/server.ts:14:    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
src/lib/supabase/client.ts:4:export function createClient() {
src/lib/supabase/client.ts:7:    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
src/lib/supabase/middleware.ts:16:    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
src/app/login/actions.ts:4:import { createClient } from "@/lib/supabase/server";
src/app/login/actions.ts:19:  const supabase = await createClient();
src/app/login/actions.ts:38:  const supabase = await createClient();
src/app/login/
… (이하 1275자 생략)
```

### 3. Bash

```
{"command": "cat src/lib/supabase/middleware.ts; sed -n 1,50p src/app/page.tsx; sed -n 20,60p \"src/app/decks/[id]/page.tsx\"; cat package.json | grep check:env; git check-ignore .env.local"}
```

결과 (앞부분):

```
Permission for this tool use was denied. It requires approval, and this session has no approval surface — nobody can answer a permission prompt here — so it was denied automatically. The action was NOT performed; do not claim it succeeded, and do not retry it: this action, and anything else that requires approval, will be denied the same way for the rest of this session. Tell the user what was blocked and why you needed it, then continue with the parts of the task that do not require approval. What required approval: This Bash command contains multiple operations. The following part requires a
… (이하 52자 생략)
```

### 4. Read

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

### 5. Read

```
{"file_path": "<사본>/src/app/page.tsx", "limit": 50}
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
… (이하 1025자 생략)
```

### 6. Read

```
{"file_path": "<사본>/src/app/decks/[id]/page.tsx", "limit": 60}
```

결과 (앞부분):

```
1	import Link from "next/link";
2	import { notFound } from "next/navigation";
3	import { createClient } from "@/lib/supabase/server";
4	import { SlidePlanSchema } from "@/lib/deck/schema";
5	import { DeckPreview } from "./deck-preview";
6	
7	type DeckRow = {
8	  id: string;
9	  company_name: string;
10	  storage_path: string;
11	  created_at: string;
12	  plan_json: unknown;
13	};
14	
15	/**
16	 * 결과 페이지. 생성이 끝나면 여기로 온다.
17	 *
18	 * 미리보기는 실제 PPTX 파일을 이미지로 렌더한 것이 아니라, 생성할 때 저장해둔
19	 * plan_json(SlidePlan)을 웹 컴포넌트로 다시 그린 것이다 — 내용은 같지만
20	 * 픽셀 단위로 PPTX와 동일하지는 않다. plan_json이 없는(이 컬럼 추가 이전에
21	 * 
… (이하 1445자 생략)
```

## 최종 답

**원인은 코드가 아니라 `.env.local`의 키입니다.** `NEXT_PUBLIC_SUPABASE_ANON_KEY` 자리에 RLS를 우회하는 service role급 키가 들어 있고, 이건 제가 고칠 수 없습니다. 앱을 실제로 띄워 재현해 보지는 못했고, 코드와 마이그레이션을 읽어서 내린 판단입니다.

**근거**
- 세션 시작 훅 검사(`check:env`)가 이 키를 service role급으로 판정했습니다. 키 값은 출력하지 않았습니다.
- RLS와 접근 제어 코드는 정상입니다.
  - `0001_init.sql`의 정책은 `auth.uid() = user_id`입니다.
  - `0003`의 예시 덱 공개 정책은 `to authenticated`로 한정돼 있어 anon은 해당되지 않습니다.
  - `proxy.ts`와 `middleware.ts`는 비로그인 사용자를 `/login`으로 보냅니다.
  - `page.tsx`와 `decks/[id]/page.tsx`는 RLS에만 의존해 조회하는데, 이것도 설계대로입니다.
- 그래서 앱은 이 키로 접속하면 정책을 전부 건너뛰고 모든 행을 읽습니다.
- `NEXT_PUBLIC_` 변수는 브라우저 번들에 그대로 들어갑니다. 이 키를 가진 사람은 누구든 Supabase REST로 `decks` 테이블 전체를 읽을 수 있습니다. 로그인 화면과 상관없이 노출되는 겁니다.

**직접 해 주셔야 할 일**
1. Supabase 대시보드의 Settings → API에서 공개용 키(`anon` 또는 `publishable`)를 복사해 `.env.local`의 `NEXT_PUBLIC_SUPABASE_ANON_KEY`에 넣으세요. `service_role`이나 `secret` 키는 안 됩니다.
2. 지금 들어 있던 키는 이미 번들에 노출됐을 수 있으니 대시보드에서 재발급(rotate)하세요.
3. `npm run check:env`가 통과하는지 확인하고, `npm run dev`를 재시작하세요.
4. 시크릿 창에서 비로그인으로 접속해 `/login`으로 넘어가는지 확인하세요.
5. 이미 다른 곳에 배포했다면 그쪽 환경변수도 같이 바꾸세요.

`.env.local`은 제가 직접 수정하지 않았습니다. 올바른 키 값을 저는 모르고, 비밀 값을 임의로 건드리는 것도 적절하지 않다고 봤습니다. 코드 변경도 없습니다.

참고로 이번 세션에서는 Bash 호출 하나가 승인 대기 중 자동 거부돼서, `package.json`의 스크립트 확인과 `.env.local`이 gitignore되는지 확인하는 단계는 못 했습니다.
