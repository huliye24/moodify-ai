-- Vanilla-PostgreSQL shim — **only** for running the RLS suite without a Supabase instance.
--
-- Supabase provides `auth.users` and `auth.uid()` from its own platform schema. A plain
-- PostgreSQL server does not, so this file creates the minimum those contracts need:
--
--   auth.users      a stand-in table for identities referenced by foreign keys
--   auth.uid()      reads the current subject the way Supabase's helper does
--                   (from `request.jwt.claims`), falling back to `moodify.uid` GUC
--   anon / authenticated   the roles Supabase's RLS policies are written against
--
-- NEVER run this against a Supabase project: it would replace the platform's `auth.uid()`.
-- The runner refuses to use it when `DATABASE_URL` does not look like a local throwaway DB
-- unless `MOODIFY_RLS_SHIM_OK=1` is explicitly set (see deployment/supabase/README.md).

create schema if not exists auth;

create table if not exists auth.users (
  id    uuid primary key,
  email text unique
);

create or replace function auth.uid()
returns uuid
language plpgsql
stable
as $$
declare
  v_claims text := current_setting('request.jwt.claims', true);
  v_sub    text;
begin
  if v_claims is not null and v_claims <> '' then
    begin
      v_sub := (v_claims::jsonb) ->> 'sub';
    exception when others then
      v_sub := null;
    end;
    if v_sub is not null and v_sub <> '' then
      return v_sub::uuid;
    end if;
  end if;
  -- 本地测试便捷通道：set local moodify.uid = '<uuid>'
  v_sub := current_setting('moodify.uid', true);
  if v_sub is null or v_sub = '' then
    return null;
  end if;
  return v_sub::uuid;
end;
$$;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin bypassrls;
  end if;
end
$$;

grant usage on schema auth to anon, authenticated, service_role;
grant select on auth.users to service_role;
