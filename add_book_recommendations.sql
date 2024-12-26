CREATE TABLE IF NOT EXISTS `mydb`.`book_recommendations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT NOT NULL,
  `receiver_id` INT NOT NULL,
  `book_id` INT NOT NULL,
  `message` VARCHAR(255),
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (`id`),
  INDEX `fk_recommendations_sender_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_recommendations_receiver_idx` (`receiver_id` ASC) VISIBLE,
  INDEX `fk_recommendations_book_idx` (`book_id` ASC) VISIBLE,
  CONSTRAINT `fk_recommendations_sender`
    FOREIGN KEY (`sender_id`)
    REFERENCES `mydb`.`users` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_recommendations_receiver`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `mydb`.`users` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_recommendations_book`
    FOREIGN KEY (`book_id`)
    REFERENCES `mydb`.`books` (`id`)
    ON DELETE CASCADE);
