-- MOOD-GENESIS-003 + MOOD-GENESIS-004 + MOOD-GENESIS-006: Contribution Network.
--
-- This migration is additive and non-destructive:
--   * Existing rows in genesis_participants are preserved; new columns are
--     nullable / defaulted so the migration never breaks deployed data.
--   * New tables follow the canonical schema in db/schema.ts and are the
--     authoritative source of truth for the Contribution Network.
--
-- Safety:
--   * No on-chain action, no token transfer, no contract deployment.
--   * No private-key handling, no wallet signing.

--> statement-breakpoint
-- Add Package 003 + 004 fields that exist in db/schema.ts but were not yet
-- materialized in the live DB. All defaults preserve existing rows.
ALTER TABLE `genesis_participants` ADD COLUMN `allocation_mood` text;--> statement-breakpoint
ALTER TABLE `genesis_participants` ADD COLUMN `allocation_atomic` text;--> statement-breakpoint
ALTER TABLE `genesis_participants` ADD COLUMN `allocation_reason` text;--> statement-breakpoint
ALTER TABLE `genesis_participants` ADD COLUMN `allocated_at` text;--> statement-breakpoint

--> statement-breakpoint
-- Add Package 003 contribution_score + Package 006 reputation_score cached
-- aggregate. Both default to 0 so existing rows remain valid.
ALTER TABLE `genesis_participants` ADD COLUMN `contribution_score` integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE `genesis_participants` ADD COLUMN `reputation_score` integer DEFAULT 0 NOT NULL;--> statement-breakpoint

--> statement-breakpoint
CREATE TABLE `contribution_tasks` (
	`id` text PRIMARY KEY NOT NULL,
	`slug` text NOT NULL,
	`title` text NOT NULL,
	`summary` text DEFAULT '' NOT NULL,
	`description` text DEFAULT '' NOT NULL,
	`category` text NOT NULL,
	`status` text DEFAULT 'draft' NOT NULL,
	`requirements` text DEFAULT '' NOT NULL,
	`evidence_instructions` text DEFAULT '' NOT NULL,
	`reward_points_default` integer DEFAULT 0 NOT NULL,
	`reward_mood_default` text,
	`reward_mood_atomic_default` text,
	`deadline` text,
	`max_approvals` integer,
	`allow_duplicate_submissions` integer DEFAULT false NOT NULL,
	`terms_version` text DEFAULT 'contribution-v1' NOT NULL,
	`created_by` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`published_at` text
);
--> statement-breakpoint
CREATE UNIQUE INDEX `contribution_tasks_slug_unique` ON `contribution_tasks` (`slug`);--> statement-breakpoint
CREATE INDEX `contribution_tasks_status_idx` ON `contribution_tasks` (`status`);--> statement-breakpoint
CREATE INDEX `contribution_tasks_category_idx` ON `contribution_tasks` (`category`);--> statement-breakpoint
CREATE INDEX `contribution_tasks_published_idx` ON `contribution_tasks` (`published_at`);--> statement-breakpoint

--> statement-breakpoint
CREATE TABLE `contribution_submissions` (
	`id` text PRIMARY KEY NOT NULL,
	`task_id` text NOT NULL,
	`participant_id` text NOT NULL,
	`status` text DEFAULT 'submitted' NOT NULL,
	`summary` text DEFAULT '' NOT NULL,
	`evidence_text` text DEFAULT '' NOT NULL,
	`evidence_urls_json` text DEFAULT '[]' NOT NULL,
	`revision_number` integer DEFAULT 1 NOT NULL,
	`submitted_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`reviewed_at` text,
	`reviewer_id` text,
	`review_note` text,
	FOREIGN KEY (`task_id`) REFERENCES `contribution_tasks`(`id`) ON UPDATE no action ON DELETE restrict,
	FOREIGN KEY (`participant_id`) REFERENCES `genesis_participants`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `contribution_submissions_task_idx` ON `contribution_submissions` (`task_id`);--> statement-breakpoint
CREATE INDEX `contribution_submissions_participant_idx` ON `contribution_submissions` (`participant_id`);--> statement-breakpoint
CREATE INDEX `contribution_submissions_status_idx` ON `contribution_submissions` (`status`);--> statement-breakpoint
CREATE INDEX `contribution_submissions_submitted_idx` ON `contribution_submissions` (`submitted_at`);--> statement-breakpoint

--> statement-breakpoint
CREATE TABLE `contribution_review_events` (
	`id` text PRIMARY KEY NOT NULL,
	`submission_id` text NOT NULL,
	`actor_id` text NOT NULL,
	`event_type` text NOT NULL,
	`old_status` text,
	`new_status` text,
	`points_delta` integer DEFAULT 0 NOT NULL,
	`reward_mood` text DEFAULT '0' NOT NULL,
	`reward_atomic` text DEFAULT '0' NOT NULL,
	`reason` text DEFAULT '' NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`submission_id`) REFERENCES `contribution_submissions`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `contribution_review_events_submission_idx` ON `contribution_review_events` (`submission_id`);--> statement-breakpoint
CREATE INDEX `contribution_review_events_actor_idx` ON `contribution_review_events` (`actor_id`);--> statement-breakpoint
CREATE INDEX `contribution_review_events_created_idx` ON `contribution_review_events` (`created_at`);--> statement-breakpoint

--> statement-breakpoint
CREATE TABLE `reputation_events` (
	`id` text PRIMARY KEY NOT NULL,
	`participant_id` text NOT NULL,
	`submission_id` text,
	`event_type` text NOT NULL,
	`points_delta` integer NOT NULL,
	`reason` text DEFAULT '' NOT NULL,
	`actor_id` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`participant_id`) REFERENCES `genesis_participants`(`id`) ON UPDATE no action ON DELETE restrict,
	FOREIGN KEY (`submission_id`) REFERENCES `contribution_submissions`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `reputation_events_participant_idx` ON `reputation_events` (`participant_id`);--> statement-breakpoint
CREATE INDEX `reputation_events_submission_idx` ON `reputation_events` (`submission_id`);--> statement-breakpoint
CREATE INDEX `reputation_events_created_idx` ON `reputation_events` (`created_at`);--> statement-breakpoint

--> statement-breakpoint
CREATE TABLE `reward_events` (
	`id` text PRIMARY KEY NOT NULL,
	`participant_id` text NOT NULL,
	`submission_id` text,
	`task_id` text,
	`reward_mood` text NOT NULL,
	`reward_atomic` text NOT NULL,
	`status` text DEFAULT 'pending' NOT NULL,
	`reason` text DEFAULT '' NOT NULL,
	`approved_by` text NOT NULL,
	`distribution_snapshot_id` text,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`participant_id`) REFERENCES `genesis_participants`(`id`) ON UPDATE no action ON DELETE restrict,
	FOREIGN KEY (`submission_id`) REFERENCES `contribution_submissions`(`id`) ON UPDATE no action ON DELETE restrict,
	FOREIGN KEY (`task_id`) REFERENCES `contribution_tasks`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `reward_events_participant_idx` ON `reward_events` (`participant_id`);--> statement-breakpoint
CREATE INDEX `reward_events_task_idx` ON `reward_events` (`task_id`);--> statement-breakpoint
CREATE INDEX `reward_events_status_idx` ON `reward_events` (`status`);--> statement-breakpoint
CREATE INDEX `reward_events_submission_idx` ON `reward_events` (`submission_id`);