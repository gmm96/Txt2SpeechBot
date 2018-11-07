--
-- Structure for table `User_Info`
--

CREATE TABLE `User_Info` (
  `row_id` int(10) NOT NULL AUTO_INCREMENT COMMENT 'Row number',
  `id` varchar(15) NOT NULL COMMENT 'User id',
  `username` varchar(32) DEFAULT NULL COMMENT 'Username',
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL COMMENT 'Second name',
  PRIMARY KEY(`id`),
  UNIQUE KEY `row_id`(`row_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Info about every user that uses at least once the bot';



--
-- Structure for table `Lan_Results`
--

CREATE TABLE `Lan_Results` (
  `row_id` int(10) NOT NULL AUTO_INCREMENT COMMENT 'Row number',
  `id` varchar(15) NOT NULL COMMENT 'User id',
  `Ar` int(11) NOT NULL DEFAULT 0 COMMENT 'Arabic',
  `De-de` int(11) NOT NULL DEFAULT 0 COMMENT 'German',
  `En-uk` int(11) NOT NULL DEFAULT 0 COMMENT 'English UK',
  `En-us` int(11) NOT NULL DEFAULT 0 COMMENT 'English US',
  `Es-es` int(11) NOT NULL DEFAULT 0 COMMENT 'Español ES',
  `Es-mx` int(11) NOT NULL DEFAULT 0 COMMENT 'Español MX',
  `Fr-fr` int(11) NOT NULL DEFAULT 0 COMMENT 'French',
  `It-it` int(11) NOT NULL DEFAULT 0 COMMENT 'Italian',
  `Pt-pt` int(11) NOT NULL DEFAULT 0 COMMENT 'Portuguese',
  `El-gr` int(11) NOT NULL DEFAULT 0 COMMENT 'Greek',
  `Ru-ru` int(11) NOT NULL DEFAULT 0 COMMENT 'Russian',
  `Tr-tr` int(11) NOT NULL DEFAULT 0 COMMENT 'Turkish',
  `Zh-cn` int(11) NOT NULL DEFAULT 0 COMMENT 'Chinese',
  `Ja` int(11) NOT NULL DEFAULT 0 COMMENT 'Japanese',
  `Pl` int(11) NOT NULL DEFAULT 0 COMMENT 'Polish',
  PRIMARY KEY(`id`),
  UNIQUE KEY `row_id`(`row_id`),
  FOREIGN KEY(`id`) REFERENCES `User_Info`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Chosen languages by user';



--
-- Structure for table `Own_Audios`
--

CREATE TABLE `Own_Audios` (
  `row_id` int(10) NOT NULL AUTO_INCREMENT COMMENT 'Row number',
  `file_id` varchar(300) NOT NULL COMMENT 'Telegram file id',
  `id` varchar(15) NOT NULL COMMENT 'User id',
  `description` varchar(30) NOT NULL COMMENT 'Short description of the audio',
  `duration` int(11) NOT NULL COMMENT 'Audio duration in seconds',
  `size` int(11) NOT NULL COMMENT 'File size in bytes',
  `times_used` int(11) NOT NULL DEFAULT 0 COMMENT 'Times that audio has been used by user',
  PRIMARY KEY(`id`, `file_id`),
  UNIQUE KEY `row_id`(`row_id`),
  FOREIGN KEY(`id`) REFERENCES `User_Info`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Stores the information of own user audios';