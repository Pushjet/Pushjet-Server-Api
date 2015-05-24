/* Please note that a lot of this was written by
 * hand so the style will be different from something
 * that's just exported using mysqldump or something.
 * Well... most of it.
 */

SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'TRADITIONAL,ALLOW_INVALID_DATES';


-- -----------------------------------------------------
-- Table `pushjet_api`.`subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pushjet_api`.`subscription`;

CREATE TABLE IF NOT EXISTS `pushjet_api`.`subscription` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `device`            VARCHAR(40)      NOT NULL,
  `service_id`        INT(10) UNSIGNED NOT NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timestamp_checked` TIMESTAMP            NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `pushjet_api`.`message`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pushjet_api`.`message`;

CREATE TABLE IF NOT EXISTS `pushjet_api`.`message` (
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
  DEFAULT CHARSET = utf8
  COLLATE = utf8_unicode_ci;

-- -----------------------------------------------------
-- Table `pushjet_api`.`service`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pushjet_api`.`service`;

CREATE TABLE IF NOT EXISTS `pushjet_api`.`service` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `secret`            VARCHAR(32)      NOT NULL,
  `public`            VARCHAR(40)      NOT NULL,
  `name`              VARCHAR(255)     NOT NULL,
  `icon`              TEXT                 NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_unicode_ci;

-- -----------------------------------------------------
-- Table `pushjet_api`.`gcm`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pushjet_api`.`gcm`;

CREATE TABLE IF NOT EXISTS `pushjet_api`.`gcm` (
  `id`                INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid`              VARCHAR(40)      NOT NULL,
  `gcmid`             TEXT             NOT NULL,
  `timestamp_created` TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_unicode_ci;

SET SQL_MODE = @OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;
