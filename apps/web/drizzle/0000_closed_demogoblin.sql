CREATE TABLE `creation_passports` (
	`id` text PRIMARY KEY NOT NULL,
	`track_version_id` text NOT NULL,
	`ai_tool` text,
	`model_version` text,
	`prompt_disclosure` text DEFAULT 'private' NOT NULL,
	`prompt_text` text,
	`lyrics_author` text,
	`vocal_source` text,
	`human_editing` text,
	`daw_tools` text,
	`collaborators` text,
	`rights_statement` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`track_version_id`) REFERENCES `track_versions`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `creation_passports_track_version_id_unique` ON `creation_passports` (`track_version_id`);--> statement-breakpoint
CREATE TABLE `creator_follows` (
	`follower_user_id` text NOT NULL,
	`creator_id` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY(`follower_user_id`, `creator_id`),
	FOREIGN KEY (`follower_user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`creator_id`) REFERENCES `creator_profiles`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `creator_follows_creator_idx` ON `creator_follows` (`creator_id`);--> statement-breakpoint
CREATE TABLE `creator_profiles` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`handle` text NOT NULL,
	`display_name` text NOT NULL,
	`bio` text DEFAULT '' NOT NULL,
	`avatar_url` text,
	`hero_image_url` text,
	`location` text,
	`is_public` integer DEFAULT true NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `creator_profiles_handle_unique` ON `creator_profiles` (`handle`);--> statement-breakpoint
CREATE UNIQUE INDEX `creator_profiles_user_unique` ON `creator_profiles` (`user_id`);--> statement-breakpoint
CREATE TABLE `license_intents` (
	`id` text PRIMARY KEY NOT NULL,
	`requester_user_id` text,
	`requester_email` text NOT NULL,
	`track_id` text NOT NULL,
	`usage_type` text NOT NULL,
	`territory` text,
	`term` text,
	`budget_range` text,
	`message` text NOT NULL,
	`status` text DEFAULT 'new' NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`requester_user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `license_intents_track_status_idx` ON `license_intents` (`track_id`,`status`);--> statement-breakpoint
CREATE TABLE `listen_events` (
	`id` text PRIMARY KEY NOT NULL,
	`track_id` text NOT NULL,
	`user_id` text,
	`anonymous_session_id` text,
	`started_at` text NOT NULL,
	`listened_ms` integer DEFAULT 0 NOT NULL,
	`completion_permille` integer DEFAULT 0 NOT NULL,
	`source_surface` text NOT NULL,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE set null
);
--> statement-breakpoint
CREATE INDEX `listen_events_track_started_idx` ON `listen_events` (`track_id`,`started_at`);--> statement-breakpoint
CREATE TABLE `publication_events` (
	`id` text PRIMARY KEY NOT NULL,
	`track_id` text NOT NULL,
	`actor_user_id` text NOT NULL,
	`from_status` text,
	`to_status` text NOT NULL,
	`reason` text,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`actor_user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `publication_events_track_created_idx` ON `publication_events` (`track_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `support_intents` (
	`id` text PRIMARY KEY NOT NULL,
	`supporter_user_id` text,
	`creator_id` text NOT NULL,
	`track_id` text,
	`amount_minor` integer,
	`currency` text,
	`provider` text,
	`provider_txn_id` text,
	`status` text DEFAULT 'intent' NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`supporter_user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`creator_id`) REFERENCES `creator_profiles`(`id`) ON UPDATE no action ON DELETE restrict,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE set null
);
--> statement-breakpoint
CREATE INDEX `support_intents_creator_status_idx` ON `support_intents` (`creator_id`,`status`);--> statement-breakpoint
CREATE TABLE `track_favorites` (
	`user_id` text NOT NULL,
	`track_id` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY(`user_id`, `track_id`),
	FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `track_favorites_track_idx` ON `track_favorites` (`track_id`);--> statement-breakpoint
CREATE TABLE `track_versions` (
	`id` text PRIMARY KEY NOT NULL,
	`track_id` text NOT NULL,
	`version_label` text NOT NULL,
	`audio_object_key` text NOT NULL,
	`audio_sha256` text NOT NULL,
	`audio_bytes` integer NOT NULL,
	`mime_type` text NOT NULL,
	`duration_ms` integer,
	`cover_object_key` text,
	`ear_production_case_id` text,
	`ear_evidence_artifact_id` text,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`track_id`) REFERENCES `tracks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `track_versions_track_label_unique` ON `track_versions` (`track_id`,`version_label`);--> statement-breakpoint
CREATE TABLE `tracks` (
	`id` text PRIMARY KEY NOT NULL,
	`creator_id` text NOT NULL,
	`title` text NOT NULL,
	`description` text DEFAULT '' NOT NULL,
	`language` text,
	`status` text DEFAULT 'draft' NOT NULL,
	`source_type` text NOT NULL,
	`license_status` text DEFAULT 'not_available' NOT NULL,
	`current_version_id` text,
	`published_at` text,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`creator_id`) REFERENCES `creator_profiles`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `tracks_creator_status_idx` ON `tracks` (`creator_id`,`status`);--> statement-breakpoint
CREATE TABLE `users` (
	`id` text PRIMARY KEY NOT NULL,
	`auth_subject` text NOT NULL,
	`email` text,
	`display_name` text NOT NULL,
	`avatar_url` text,
	`status` text DEFAULT 'active' NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `users_auth_subject_unique` ON `users` (`auth_subject`);--> statement-breakpoint
CREATE UNIQUE INDEX `users_email_unique` ON `users` (`email`);