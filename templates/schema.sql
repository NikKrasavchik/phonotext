-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;

CREATE TABLE `user` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`username`	TEXT,
	`password`	TEXT NOT NULL,
	`email`	TEXT NOT NULL UNIQUE,
	`age` INTEGER DEFAULT 0,
	`status` INTEGER DEFAULT 0,
	`accesslvl`	INTEGER DEFAULT 0
);

INSERT INTO `user` (`username`, `email`, `password`, `accesslvl`) VALUES ("admin", "admin","pbkdf2:sha256:50000$lj73DK91$5955149bd86cf9ddd6133e6b91229aead94322830ffb55c225841f915bba8861", 101);
INSERT INTO `user` (`username`, `email`, `password`, `accesslvl`) VALUES ("test", "test", "pbkdf2:sha256:50000$FUcgRvWY$9bc3ce311dd090189bb8b897b90951f14a108ec9e5390dda3a38980109329a4b", 0);

