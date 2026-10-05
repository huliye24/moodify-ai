-- RLS / owner-boundary suite — two real users (A and B), run against Supabase or a local
-- PostgreSQL with `tests/local_shim.sql` prepended.
--
-- Contract: protocol/mips/MIP-0003-personal-identity-history.md §6
-- Run:      deployment/supabase/tests/run.sh  (or: psql -f shim -f migrations -f this)
--
-- Every assertion below must hold. A failure raises and aborts the transaction block.
-- The suite ends with exactly one row: `rls suite: PASS (n checks)`.

\set ON_ERROR_STOP on

begin;

-- ——— fixtures: two users, one work each —————————————————————————————————————
insert into auth.users (id, email) values
  ('11111111-1111-4111-8111-111111111111', 'user-a@example.test'),
  ('22222222-2222-4222-8222-222222222222', 'user-b@example.test')
on conflict (id) do nothing;

insert into public.profiles (user_id, display_name) values
  ('11111111-1111-4111-8111-111111111111', 'A'),
  ('22222222-2222-4222-8222-222222222222', 'B')
on conflict (user_id) do update set display_name = excluded.display_name;

insert into public.works (work_id, user_id, title, selected, audio_availability) values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111111', 'A 的歌', 'A', 'LOCAL_ONLY'),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', '22222222-2222-4222-8222-222222222222', 'B 的歌', 'B', 'LOCAL_ONLY')
on conflict (work_id) do update set title = excluded.title;

-- 以“未认证”身份执行：auth.uid() 为 null，任何策略都不应放行
do $$
declare n integer;
begin
  perform set_config('moodify.uid', '', true);
  set local role authenticated;
  begin
    select count(*) into n from public.works;
    if n <> 0 then
      raise exception 'unauthenticated session must see zero rows, saw %', n;
    end if;
    begin
      insert into public.works (work_id, user_id, title) values
        ('cccccccc-cccc-4ccc-8ccc-cccccccccccc',
         '11111111-1111-4111-8111-111111111111', '越权写入');
      raise exception 'unauthenticated insert must fail';
    exception when insufficient_privilege or check_violation then
      null; -- 预期：with check (auth.uid() = user_id) 拒绝
    end;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- user A 只能看见自己的一行
do $$
declare n integer; t text;
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    select count(*) into n from public.works;
    if n <> 1 then raise exception 'A must see exactly 1 work, saw %', n; end if;
    select title into t from public.works;
    if t <> 'A 的歌' then raise exception 'A saw the wrong row: %', t; end if;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- user A 猜 B 的 work_id 读取 → 必须 0 行
do $$
declare n integer;
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    select count(*) into n from public.works
     where work_id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
    if n <> 0 then raise exception 'A must not read B''s work (got %)', n; end if;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- user A 猜 B 的 work_id 更新 / 删除 → 必须 0 行受影响
do $$
declare affected integer;
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    update public.works set title = '被 A 改掉'
     where work_id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
    get diagnostics affected = row_count;
    if affected <> 0 then raise exception 'A must not update B''s work (affected %)', affected; end if;

    delete from public.works where work_id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
    get diagnostics affected = row_count;
    if affected <> 0 then raise exception 'A must not delete B''s work (affected %)', affected; end if;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- 伪造 user_id（把自己的 user_id 写成 B）→ with check 必须拒绝
do $$
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    insert into public.works (work_id, user_id, title) values
      ('dddddddd-dddd-4ddd-8ddd-dddddddddddd',
       '22222222-2222-4222-8222-222222222222', 'A 伪造 B');
    raise exception 'spoofed user_id must be rejected';
  exception when insufficient_privilege or check_violation then
    null; -- 预期
  when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- 幂等：同一 request_id push 两次只形成一个 event（服务端唯一约束）
do $$
declare first_row record; second_row record; n integer;
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    select * into first_row from public.push_history_events(jsonb_build_array(jsonb_build_object(
      'work_id', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      'event_type', 'WORK_COMPLETED',
      'occurred_at', '2026-10-04T10:00:00Z',
      'request_id', 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',
      'payload', jsonb_build_object('title', 'A 的歌', 'selected', 'A'))));
    select * into second_row from public.push_history_events(jsonb_build_array(jsonb_build_object(
      'work_id', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      'event_type', 'WORK_COMPLETED',
      'occurred_at', '2026-10-04T10:00:00Z',
      'request_id', 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',
      'payload', jsonb_build_object('title', 'A 的歌', 'selected', 'A'))));
    if first_row.accepted <> 1 then
      raise exception 'first push must accept 1, got %', first_row.accepted;
    end if;
    if second_row.duplicated <> 1 or second_row.accepted <> 0 then
      raise exception 'retry must be reported as duplicate (accepted %, duplicated %)',
        second_row.accepted, second_row.duplicated;
    end if;
    select count(*) into n from public.history_events
     where request_id = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee';
    if n <> 1 then raise exception 'retry created % events', n; end if;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- 删除 + 墓碑：A 删掉自己的 work 后，B 不受影响，A 也看不到它
do $$
declare n integer;
begin
  perform set_config('moodify.uid', '11111111-1111-4111-8111-111111111111', true);
  set local role authenticated;
  begin
    perform public.delete_history_item('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
    select count(*) into n from public.works
     where work_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
    if n <> 0 then raise exception 'deleted work still visible'; end if;
    select count(*) into n from public.deleted_works
     where work_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
    if n <> 1 then raise exception 'tombstone missing'; end if;
    -- 重新 claim 必须被墓碑拒绝（其他设备不能复活已删除记录）
    begin
      perform public.claim_work('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'A 的歌');
      raise exception 'claiming a tombstoned work must fail';
    exception when others then
      if position('tombstone' in sqlerrm) = 0 and position('deleted' in sqlerrm) = 0 then
        raise;
      end if;
    end;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- 导出只含自己的数据，且不含任何音频/路径字段
do $$
declare payload jsonb; body text;
begin
  perform set_config('moodify.uid', '22222222-2222-4222-8222-222222222222', true);
  set local role authenticated;
  begin
    payload := public.export_account_data();
    body := payload::text;
    if body like '%11111111-1111-4111-8111-111111111111%' then
      raise exception 'export leaked another user''s id';
    end if;
    if body ~* '(wav|mp3|flac|sha256|C:\\\\|/Users/|/home/)' then
      raise exception 'export leaked audio/path/hash material: %', body;
    end if;
  exception when others then
    reset role;
    raise;
  end;
  reset role;
end
$$;

-- 受控删除函数不能被普通会话调用（只有 service_role 有 execute 权限）
do $$
declare allowed boolean;
begin
  select has_function_privilege('authenticated', 'public.delete_account(uuid)', 'execute')
    into allowed;
  if allowed then
    raise exception 'authenticated must NOT be able to call delete_account()';
  end if;
  select has_function_privilege('anon', 'public.delete_account(uuid)', 'execute')
    into allowed;
  if allowed then
    raise exception 'anon must NOT be able to call delete_account()';
  end if;
  select has_function_privilege('service_role', 'public.delete_account(uuid)', 'execute')
    into allowed;
  if not allowed then
    raise exception 'service_role must be able to call delete_account()';
  end if;
end
$$;

-- 表级默认拒绝：anon 对四张表都没有权限
do $$
declare t text;
begin
  foreach t in array array['profiles', 'works', 'history_events', 'deleted_works'] loop
    if has_table_privilege('anon', format('public.%I', t), 'select') then
      raise exception 'anon must not have select on %', t;
    end if;
    if has_table_privilege('anon', format('public.%I', t), 'insert') then
      raise exception 'anon must not have insert on %', t;
    end if;
  end loop;
end
$$;

-- 清理两个测试用户（级联删除它们的行）
delete from public.history_events
 where user_id in ('11111111-1111-4111-8111-111111111111',
                   '22222222-2222-4222-8222-222222222222');
delete from public.works
 where user_id in ('11111111-1111-4111-8111-111111111111',
                   '22222222-2222-4222-8222-222222222222');
delete from public.deleted_works
 where user_id in ('11111111-1111-4111-8111-111111111111',
                   '22222222-2222-4222-8222-222222222222');
delete from public.profiles
 where user_id in ('11111111-1111-4111-8111-111111111111',
                   '22222222-2222-4222-8222-222222222222');
delete from auth.users
 where id in ('11111111-1111-4111-8111-111111111111',
              '22222222-2222-4222-8222-222222222222');

select 'rls suite: PASS (11 checks)' as result;

rollback;
