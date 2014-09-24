CREATE TABLE `user` (
  `id` INTEGER PRIMARY KEY,
  `name` TEXT,
  `nick_name` TEXT,
  `avator` TEXT
);
CREATE UNIQUE INDEX idx_username ON user(name);

CREATE TABLE `question` (
  `id` INTEGER PRIMARY KEY,
  `title` TEXT,
  `description` TEXT,
  `create_time` INTEGER
);
CREATE UNIQUE INDEX idx_title ON question(title);

CREATE TABLE `answer` (
  `id` INTEGER PRIMARY KEY,
  `q_id` INTEGER,
  `user_id` TEXT,
  `text` TEXT,
  `create_time` INTEGER
);
CREATE UNIQUE INDEX idx_qu ON answer(q_id, user_id);
