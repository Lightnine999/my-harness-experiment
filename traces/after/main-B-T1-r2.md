# main-B-T1-r2

| 항목 | 값 |
|---|---|
| 조건 | B (SessionStart 훅 있음) |
| 과업 | T1 (키 문제) |
| AGENTS.md `NEXT_PUBLIC_` 절 | 뺌 |
| 모델 | claude-sonnet-5-5 |
| 턴 · 도구 호출 | 6 · 5 |
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

### 1. Grep

```
{"pattern": "createClient|createServerClient|service_role|SERVICE_ROLE|ANON_KEY", "path": "<사본>", "glob": "!node_modules/**", "output_mode": "content", "head_limit": 50}
```

결과 (앞부분):

```
README.md:58:| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 같은 화면의 **publishable** 키 | 비밀 키를 넣으면 안 됩니다 |
scripts/check-env.ts:5: * 배경: 2026-09-08에 NEXT_PUBLIC_SUPABASE_ANON_KEY 자리에 service role급
scripts/check-env.ts:36:      note: "이 키는 RLS를 우회합니다. NEXT_PUBLIC_SUPABASE_ANON_KEY 자리에 있으면 안 됩니다.",
scripts/check-env.ts:44:    if (role === "service_role") {
scripts/check-env.ts:46:        name: "레거시 JWT service_role",
scripts/check-env.ts:48:        note: "service_role 키가 anon 자리에 들어가 있습니다. RLS가 전부 우회됩니다.",
scripts/check-env.ts:70:  const key = (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "").trim();
scripts
… (이하 2118자 생략)
```

### 2. Glob

```
{"pattern": "supabase/migrations/*", "path": "<사본>"}
```

결과 (앞부분):

```
supabase/migrations/0001_init.sql
supabase/migrations/0003_add_example_decks.sql
supabase/migrations/0002_add_plan_json.sql
```

### 3. Bash

```
{"command": "ls -a | head -50 && sed -E 's/=.*/=<hidden>/' .env.local 2>/dev/null"}
```

결과 (앞부분):

```
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
NEXT_PUBLIC_SUPABASE_URL=<hidden>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<hidden>
BACKEND_URL=<hidden>
BACKEND_SECRET=<hidden>
```

### 4. Bash

```
{"command": "cat supabase/migrations/*.sql && cat src/app/page.tsx src/proxy.ts src/lib/supabase/middleware.ts"}
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
  for select using (auth.uid() = user_id);

create policy "decks_insert_own" on public.decks
  for insert with check (auth.uid() = user_id);

create policy "decks_delete_own"
… (이하 7776자 생략)
```

### 5. Bash

```
{"command": "sed -n 15,60p \"src/app/decks/[id]/page.tsx\"; sed -n 1,30p src/app/decks/actions.ts; sed -n 1,40p scripts/add-example-deck.ts"}
```

결과 (앞부분):

```
/**
 * 결과 페이지. 생성이 끝나면 여기로 온다.
 *
 * 미리보기는 실제 PPTX 파일을 이미지로 렌더한 것이 아니라, 생성할 때 저장해둔
 * plan_json(SlidePlan)을 웹 컴포넌트로 다시 그린 것이다 — 내용은 같지만
 * 픽셀 단위로 PPTX와 동일하지는 않다. plan_json이 없는(이 컬럼 추가 이전에
 * 만들어진) 기존 덱은 자리표시자로 대체한다.
 */
export default async function DeckPage({
  params,
}: PageProps<"/decks/[id]">) {
  const { id } = await params;
  const supabase = await createClient();

  // RLS(decks_select_own)가 본인 소유 행만 돌려주므로 별도 소유권 검사가 필요 없다.
  const { data: deck } = await supabase
    .from("decks")
    .select("id, company_name, storage_path, created_at, plan_json")
    .eq("id", id)
    .maybeSingle<D
… (이하 2916자 생략)
```

## 최종 답

원인은 코드나 RLS 정책이 아니라 `.env.local`의 키입니다. 코드는 건드리지 않았고, 고치려면 키를 직접 바꿔 주셔야 합니다.

**원인**
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` 자리에 secret 키(service role급)가 들어 있습니다. 세션 시작 훅의 `check:env`가 이 키를 잡아냈습니다. 길이는 42자입니다.
- secret 키는 RLS를 전부 우회합니다. 그래서 `decks_select_own` 같은 정책이 있어도 모든 사용자의 자료가 조회됩니다.
- `NEXT_PUBLIC_` 접두사가 붙은 변수라 이 키는 브라우저 번들에도 실립니다. 누구나 키를 꺼내 DB를 직접 읽을 수 있는 상태입니다.

**확인한 것**
- `supabase/migrations/0001~0003`의 RLS 정책은 올바릅니다. `decks_select_examples`도 `to authenticated`로 한정돼 있어서 비로그인 방문자는 포함되지 않습니다.
- `src/proxy.ts`와 `middleware.ts`는 비로그인 접근을 `/login`으로 보냅니다.
- `page.tsx`, `decks/[id]/page.tsx`, `actions.ts`는 모두 RLS에 의존하는 구조라 키만 바로잡으면 정상 동작합니다.

**고치는 방법**
1. Supabase 대시보드의 API Keys 화면에서 **publishable** 키(`sb_publishable_...`)나 레거시 `anon` 키를 복사합니다.
2. `.env.local`의 `NEXT_PUBLIC_SUPABASE_ANON_KEY` 값을 그 키로 바꿉니다. 저는 값을 알 수 없고 비밀 키를 다루지 않으려고 직접 수정하지 않았습니다.
3. 기존 secret 키는 **이미 노출됐다고 보고 폐기 후 재발급**하세요. 브라우저 번들에 실렸을 수 있고, 키가 git 기록이나 로그에 남았다면 그쪽도 확인이 필요합니다.
4. `npm run check:env`가 통과하는지 확인하고 dev 서버를 재시작합니다. 로그아웃 상태에서 `/`가 `/login`으로 가는지, 다른 계정 자료가 안 보이는지 봐 주세요.

원하시면 `predev`/`prebuild`에 `check:env`를 걸어, 이 키가 있으면 서버가 아예 뜨지 않게 하는 안전장치를 추가하겠습니다.
