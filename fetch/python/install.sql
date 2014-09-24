CREATE TABLE `user` (
  `id` INTEGER PRIMARY KEY,
  `name` TEXT NOT NULL,
  `nick_name` TEXT NOT NULL DEFAULT '',
  `avatar` TEXT NOT NULL DEFAULT '',
  `fetch_time` INTEGER NOT NULL DEFAULT 0,
  `fetch` INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX idx_username ON user(name);

CREATE TABLE `question` (
  `id` INTEGER PRIMARY KEY,
  `title` TEXT NOT NULL,
  `description` TEXT NOT NULL,
  `fetch_time` INTEGER NOT NULL DEFAULT 0,
  `fetch` INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE `answer` (
  `id` INTEGER PRIMARY KEY,
  `q_id` INTEGER NOT NULL,
  `user_id` INTEGER NOT NULL,
  `text` TEXT NOT NULL,
  `vote` INTEGER NOT NULL,
  `fetch_time` INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX idx_qu ON answer(q_id, user_id);
