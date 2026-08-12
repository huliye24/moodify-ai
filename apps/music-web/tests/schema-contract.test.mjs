import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const schemaPath = new URL("../db/schema.ts", import.meta.url);
const migrationPath = new URL("../drizzle/0000_closed_demogoblin.sql", import.meta.url);

test("commercial schema has one explicit authority for all v1 entities", async () => {
  const schema = await readFile(schemaPath, "utf8");
  const required = [
    "users", "creator_profiles", "tracks", "track_versions",
    "creation_passports", "creator_follows", "track_favorites",
    "license_intents", "support_intents", "listen_events",
    "publication_events",
  ];
  for (const table of required) {
    assert.match(schema, new RegExp(`sqliteTable\\(\\"${table}\\"`), table);
  }
});

test("migration preserves relationship uniqueness and evidence separation", async () => {
  const sql = await readFile(migrationPath, "utf8");
  assert.match(sql, /PRIMARY KEY\(`follower_user_id`, `creator_id`\)/);
  assert.match(sql, /PRIMARY KEY\(`user_id`, `track_id`\)/);
  assert.match(sql, /`ear_production_case_id` text/);
  assert.doesNotMatch(sql, /audio_blob|measurement_record|job_id/);
});

test("media bindings are declared without credentials", async () => {
  const hosting = JSON.parse(await readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"));
  assert.deepEqual(hosting, { d1: "DB", r2: "MEDIA" });
});
