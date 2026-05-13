-- ==================== LEAGUE STANDINGS ====================
-- Generated: 2026-04-10 10:15:56

CREATE TABLE IF NOT EXISTS `standings` (
  `position` INT PRIMARY KEY,
  `team` VARCHAR(100) NOT NULL,
  `games` INT DEFAULT 0,
  `wins` INT DEFAULT 0,
  `draws` INT DEFAULT 0,
  `losses` INT DEFAULT 0,
  `goals_for` INT DEFAULT 0,
  `goals_against` INT DEFAULT 0,
  `goal_difference` INT DEFAULT 0,
  `points` INT DEFAULT 0
);

DELETE FROM `standings`;

-- ==================== INSERT DATA ====================
INSERT INTO `standings` (`position`, `team`, `games`, `wins`, `draws`, `losses`, `goals_for`, `goals_against`, `goal_difference`, `points`) VALUES
(1, 'PSV Eindhoven', 29, 23, 2, 4, 82, 40, 42, 71),
(2, 'Feyenoord', 29, 16, 6, 7, 61, 40, 21, 54),
(3, 'Nijmegen', 29, 15, 8, 6, 71, 47, 24, 53),
(4, 'Twente', 29, 13, 11, 5, 49, 31, 18, 50),
(5, 'Ajax', 29, 12, 12, 5, 54, 37, 17, 48),
(6, 'AZ Alkmaar', 29, 13, 6, 10, 49, 45, 4, 45),
(7, 'Heerenveen', 29, 12, 8, 9, 53, 47, 6, 44),
(8, 'Sparta Rotterdam', 29, 12, 6, 11, 35, 47, -12, 42),
(9, 'Utrecht', 29, 11, 8, 10, 45, 35, 10, 41),
(10, 'Groningen', 29, 12, 5, 12, 42, 37, 5, 41),
(11, 'Go Ahead Eagles', 29, 8, 11, 10, 50, 45, 5, 35),
(12, 'For Sittard', 29, 10, 5, 14, 43, 54, -11, 35),
(13, 'Zwolle', 29, 8, 9, 12, 38, 58, -20, 33),
(14, 'Volendam', 29, 7, 7, 15, 30, 48, -18, 28),
(15, 'Telstar', 29, 6, 9, 14, 38, 48, -10, 27),
(16, 'Excelsior', 29, 7, 6, 16, 29, 49, -20, 27),
(17, 'NAC Breda', 29, 5, 9, 15, 29, 50, -21, 24),
(18, 'Heracles', 29, 5, 4, 20, 34, 74, -40, 19);
