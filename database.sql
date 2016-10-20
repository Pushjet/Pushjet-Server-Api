SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'TRADITIONAL,ALLOW_INVALID_DATES';


-- -----------------------------------------------------
-- Table `subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `subscription`;

CREATE TABLE IF NOT EXISTS `subscription` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `device`            VARCHAR(40)      NOT NULL,
  `service_id`        INT(10) UNSIGNED NOT NULL,
  `last_read`         INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timestamp_checked` TIMESTAMP            NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- -----------------------------------------------------
-- Table `message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `message`;

CREATE TABLE IF NOT EXISTS `message` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `service_id`        INT(10) UNSIGNED NOT NULL,
  `text`              TEXT             NOT NULL,
  `title`             VARCHAR(255)         NULL  DEFAULT NULL,
  `level`             TINYINT(4)       NOT NULL DEFAULT '0',
  `link`              TEXT                 NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `service`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `service`;

CREATE TABLE IF NOT EXISTS `service` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `secret`            VARCHAR(32)      NOT NULL,
  `public`            VARCHAR(40)      NOT NULL,
  `name`              VARCHAR(255)     NOT NULL,
  `icon`              TEXT                 NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `gcm`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `gcm`;

CREATE TABLE IF NOT EXISTS `gcm` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid`              VARCHAR(40)      NOT NULL,
  `gcmid`             TEXT             NOT NULL,
  `pubkey`            TEXT             DEFAULT NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rsa_pub`           BLOB(1024)       DEFAULT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

SET SQL_MODE = @OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;
