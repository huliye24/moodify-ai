CREATE TABLE `genesis_nonces` (
	`id` text PRIMARY KEY NOT NULL,
	`wallet_address_normalized` text NOT NULL,
	`nonce_hash` text NOT NULL,
	`issued_at` text NOT NULL,
	`expires_at` text NOT NULL,
	`used_at` text,
	`chain_id` integer NOT NULL,
	`terms_version` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `genesis_nonces_nonce_hash_unique` ON `genesis_nonces` (`nonce_hash`);--> statement-breakpoint
CREATE INDEX `genesis_nonces_wallet_idx` ON `genesis_nonces` (`wallet_address_normalized`);--> statement-breakpoint
CREATE INDEX `genesis_nonces_expires_idx` ON `genesis_nonces` (`expires_at`);--> statement-breakpoint
CREATE TABLE `genesis_participants` (
	`id` text PRIMARY KEY NOT NULL,
	`participant_number` integer NOT NULL,
	`wallet_address` text NOT NULL,
	`wallet_address_normalized` text NOT NULL,
	`chain_id` integer NOT NULL,
	`joined_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`status` text DEFAULT 'registered' NOT NULL,
	`signature_version` text NOT NULL,
	`terms_version` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `genesis_participants_participant_number_unique` ON `genesis_participants` (`participant_number`);--> statement-breakpoint
CREATE UNIQUE INDEX `genesis_participants_wallet_address_normalized_unique` ON `genesis_participants` (`wallet_address_normalized`);--> statement-breakpoint
CREATE INDEX `genesis_participants_wallet_idx` ON `genesis_participants` (`wallet_address_normalized`);--> statement-breakpoint
CREATE INDEX `genesis_participants_joined_idx` ON `genesis_participants` (`joined_at`);