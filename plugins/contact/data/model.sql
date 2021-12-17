
CREATE TABLE IF NOT EXISTS `contact_channels` (
  `guild` BIGINT NOT NULL,
  `channel` BIGINT PRIMARY KEY NOT NULL,
  `author` BIGINT NOT NULL,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_contactchannels_guild ON `contact_channels` (`guild`);

CREATE TABLE IF NOT EXISTS `contact_topics` (
  `guild` BIGINT NOT NULL,
  `title` TEXT PRIMARY KEY NOT NULL,
  `description` TEXT NOT NULL,
  `emoji` TEXT
);
CREATE INDEX IF NOT EXISTS idx_contacttopics_guild ON `contact_topics` (`guild`);
