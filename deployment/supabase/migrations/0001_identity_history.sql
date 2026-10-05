-- Moodify Phase 3A — Identity / Account / Personal History
-- Migration 0001: tables, RLS, owner boundary, controlled deletion.
--
-- Contract: protocol/mips/MIP-0003-personal-identity-history.md
-- Authority: this SQL is the authoritative cloud data model. `works` is a *projection* of
-- `history_events`, not a second source of truth, and neither is ever the authority for the
-- local sound-production facts (local case dir + Core artifacts stay authoritative).
--
-- Nothing here may ever hold audio, stems, MIDI, scores, reports, spectra, Mix Graph
-- parameters, local paths, source hashes, tokens or credentials. See §3 of the MIP.

-- ——— tables ————————————————————————————————————————————————————————————————

create table if not exists public.profiles (
  user_id      uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

comment on table public.profiles is
  'Account-private profile. Phase 3A: no avatar upload, no username squatting, no public profile.';

create table if not exists public.works (
  work_id            uuid primary key,
  user_id            uuid not null references auth.users (id) on delete cascade,
  title              text not null check (char_length(title) between 1 and 300),
  duration_ms        bigint check (duration_ms is null or duration_ms >= 0),
  completion_mode    text check (completion_mode is null
                                 or completion_mode in ('DEEP', 'FAST_STEREO_ONLY')),
  selected           text check (selected is null or selected in ('A', 'B', 'ORIGINAL')),
  completed_at       timestamptz,
  inscription        text check (inscription is null or char_length(inscription) <= 280),
  -- 产品事实：云端永远不持有音频。这一列不是可配置项。
  audio_availability text not null default 'LOCAL_ONLY' check (audio_availability = 'LOCAL_ONLY'),
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  revision           bigint not null default 0
);

create index if not exists works_user_completed_idx
  on public.works (user_id, completed_at desc nulls last, work_id);

create table if not exists public.history_events (
  event_id           uuid primary key default gen_random_uuid(),
  user_id            uuid not null references auth.users (id) on delete cascade,
  work_id            uuid not null,
  event_type         text not null check (event_type in (
                       'WORK_COMPLETED', 'DECISION_CHANGED', 'INSCRIPTION_UPDATED',
                       'AUDIO_EXPORTED', 'WORK_REVISITED')),
  occurred_at        timestamptz not null,
  client_id          uuid,
  request_id         uuid not null,
  schema_version     text not null default 'moodify.studio.history-event/0.1',
  payload            jsonb not null default '{}'::jsonb,
  server_received_at timestamptz not null default now(),
  -- 幂等：同一个 request_id 重试只形成一个 event
  unique (user_id, request_id)
);

create index if not exists history_events_user_work_idx
  on public.history_events (user_id, work_id, server_received_at, event_id);
create index if not exists history_events_user_received_idx
  on public.history_events (user_id, server_received_at, event_id);

comment on column public.history_events.payload is
  'Whitelisted per event type (moodify-desktop/src/history-sync/schema.js). Never a telemetry dump.';

-- 墓碑：删除过的 work 不得因为其他设备的下一次 pull 而复活（MIP §5 删除语义）。
create table if not exists public.deleted_works (
  user_id    uuid not null references auth.users (id) on delete cascade,
  work_id    uuid not null,
  deleted_at timestamptz not null default now(),
  primary key (user_id, work_id)
);

-- ——— RLS: default deny, owner-only ——————————————————————————————————————————
--
-- 客户端传入的 user_id 从不被信任：insert 由 with check 校验，update 不允许改 user_id。

alter table public.profiles       enable row level security;
alter table public.works          enable row level security;
alter table public.history_events enable row level security;
alter table public.deleted_works  enable row level security;

-- 默认拒绝：先撤销所有权限，再按策略放开（anon 什么也拿不到）
revoke all on public.profiles       from anon, authenticated;
revoke all on public.works          from anon, authenticated;
revoke all on public.history_events from anon, authenticated;
revoke all on public.deleted_works  from anon, authenticated;

grant select, insert, update on public.profiles       to authenticated;
grant select, insert, update on public.works          to authenticated;
grant select, insert          on public.history_events to authenticated;
grant select                  on public.deleted_works  to authenticated;

drop policy if exists profiles_owner on public.profiles;
create policy profiles_owner on public.profiles
  for all to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists works_owner on public.works;
create policy works_owner on public.works
  for all to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists history_events_owner on public.history_events;
create policy history_events_owner on public.history_events
  for all to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- 墓碑只读：写墓碑由受控函数完成
drop policy if exists deleted_works_owner_read on public.deleted_works;
create policy deleted_works_owner_read on public.deleted_works
  for select to authenticated
  using (auth.uid() = user_id);

-- ——— 受控写入路径 ——————————————————————————————————————————————————————————
--
-- Desktop 只能调用这些函数；它没有 service-role key，也不能直接改 user_id。

-- append-only push：按 (user_id, request_id) 幂等；works 投影在同一事务内更新。
create or replace function public.push_history_events(p_events jsonb)
returns table (accepted integer, duplicated integer, cursor timestamptz)
language plpgsql
security invoker
set search_path = public
as $$
declare
  v_uid    uuid := auth.uid();
  v_event  jsonb;
  v_ok     integer := 0;
  v_dup    integer := 0;
  v_cursor timestamptz;
begin
  if v_uid is null then
    raise exception 'not authenticated' using errcode = '28000';
  end if;

  for v_event in select * from jsonb_array_elements(coalesce(p_events, '[]'::jsonb)) loop
    begin
      insert into public.history_events (
        user_id, work_id, event_type, occurred_at, client_id, request_id, schema_version, payload
      ) values (
        v_uid,
        (v_event ->> 'work_id')::uuid,
        v_event ->> 'event_type',
        coalesce((v_event ->> 'occurred_at')::timestamptz, now()),
        nullif(v_event ->> 'client_id', '')::uuid,
        (v_event ->> 'request_id')::uuid,
        coalesce(v_event ->> 'schema_version', 'moodify.studio.history-event/0.1'),
        coalesce(v_event -> 'payload', '{}'::jsonb)
      );
      v_ok := v_ok + 1;
    exception when unique_violation then
      -- 重试不是错误：同一个 request_id 只形成一个 event
      v_dup := v_dup + 1;
    end;

    -- works 投影：只在确实属于本用户、且未被墓碑删除时更新
    insert into public.works as w (
      work_id, user_id, title, duration_ms, completion_mode, selected,
      completed_at, inscription, revision
    ) values (
      (v_event ->> 'work_id')::uuid,
      v_uid,
      coalesce(nullif(v_event -> 'payload' ->> 'title', ''), '未命名作品'),
      nullif(v_event -> 'payload' ->> 'duration_ms', '')::bigint,
      nullif(v_event -> 'payload' ->> 'completion_mode', ''),
      nullif(v_event -> 'payload' ->> 'selected', ''),
      nullif(v_event -> 'payload' ->> 'completed_at', '')::timestamptz,
      nullif(v_event -> 'payload' ->> 'inscription', ''),
      coalesce((v_event ->> 'revision')::bigint, 0)
    )
    on conflict (work_id) do update set
      title           = coalesce(excluded.title, w.title),
      duration_ms     = coalesce(excluded.duration_ms, w.duration_ms),
      completion_mode = coalesce(excluded.completion_mode, w.completion_mode),
      selected        = coalesce(excluded.selected, w.selected),
      completed_at    = coalesce(excluded.completed_at, w.completed_at),
      inscription     = coalesce(excluded.inscription, w.inscription),
      revision        = greatest(w.revision, excluded.revision),
      updated_at      = now()
    where w.user_id = v_uid;
  end loop;

  select max(server_received_at) into v_cursor
    from public.history_events where user_id = v_uid;

  return query select v_ok, v_dup, v_cursor;
end;
$$;

-- 本地 case 认领：把 work_id 明确绑定到本账户（首次同步确认后的动作，幂等）
create or replace function public.claim_work(p_work_id uuid, p_title text)
returns public.works
language plpgsql
security invoker
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_row public.works;
begin
  if v_uid is null then
    raise exception 'not authenticated' using errcode = '28000';
  end if;
  if exists (select 1 from public.deleted_works d
              where d.user_id = v_uid and d.work_id = p_work_id) then
    raise exception 'work was deleted on the server' using errcode = 'P0001';
  end if;
  insert into public.works (work_id, user_id, title)
  values (p_work_id, v_uid, coalesce(nullif(p_title, ''), '未命名作品'))
  on conflict (work_id) do update set updated_at = now()
  where public.works.user_id = v_uid
  returning * into v_row;
  return v_row;
end;
$$;

-- 删除单个云端历史项：硬删除 works + history_events，写墓碑防复活
create or replace function public.delete_history_item(p_work_id uuid)
returns void
language plpgsql
security invoker
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'not authenticated' using errcode = '28000';
  end if;
  delete from public.history_events where user_id = v_uid and work_id = p_work_id;
  delete from public.works          where user_id = v_uid and work_id = p_work_id;
  insert into public.deleted_works (user_id, work_id) values (v_uid, p_work_id)
  on conflict (user_id, work_id) do update set deleted_at = now();
end;
$$;

-- 账户数据导出：服务端当前账户数据，不含任何未上传的本地内容
create or replace function public.export_account_data()
returns jsonb
language sql
security invoker
set search_path = public
stable
as $$
  select jsonb_build_object(
    'schema', 'moodify.account-export/0.1',
    'exported_at', now(),
    'profile', (select to_jsonb(p) from public.profiles p where p.user_id = auth.uid()),
    'works', coalesce((select jsonb_agg(to_jsonb(w) order by w.completed_at desc nulls last)
                         from public.works w where w.user_id = auth.uid()), '[]'::jsonb),
    'history_events', coalesce((select jsonb_agg(to_jsonb(e) order by e.server_received_at, e.event_id)
                                  from public.history_events e where e.user_id = auth.uid()), '[]'::jsonb)
  );
$$;

-- 删除账户：唯一允许触碰 auth.users 的路径。security definer + 只授予 service_role，
-- 因此普通 anon/authenticated 会话无法调用（MIP §6 / 任务包 §12.3）。
create or replace function public.delete_account(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from public.history_events where user_id = p_user_id;
  delete from public.works          where user_id = p_user_id;
  delete from public.deleted_works  where user_id = p_user_id;
  delete from public.profiles       where user_id = p_user_id;
  delete from auth.users            where id = p_user_id;
end;
$$;

revoke all on function public.delete_account(uuid) from public, anon, authenticated;
grant execute on function public.delete_account(uuid) to service_role;

grant execute on function public.push_history_events(jsonb) to authenticated;
grant execute on function public.claim_work(uuid, text)      to authenticated;
grant execute on function public.delete_history_item(uuid)   to authenticated;
grant execute on function public.export_account_data()       to authenticated;
