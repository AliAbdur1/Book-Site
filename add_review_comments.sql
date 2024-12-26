-- Create review_comments table
CREATE TABLE IF NOT EXISTS `mydb`.`review_comments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `comment` VARCHAR(500) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT NOT NULL,
  `review_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_review_comments_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_review_comments_reviews1_idx` (`review_id` ASC) VISIBLE,
  CONSTRAINT `fk_review_comments_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_review_comments_reviews1`
    FOREIGN KEY (`review_id`)
    REFERENCES `mydb`.`reviews` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
