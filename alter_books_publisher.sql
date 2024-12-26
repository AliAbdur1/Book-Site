-- First, drop the existing foreign key constraint
ALTER TABLE `mydb`.`books` 
DROP FOREIGN KEY `fk_books_publishers1`;

-- Then modify the publisher_id column to allow NULL values
ALTER TABLE `mydb`.`books` 
MODIFY COLUMN `publisher_id` INT NULL;

-- Finally, add back the foreign key constraint with SET NULL on delete
ALTER TABLE `mydb`.`books` 
ADD CONSTRAINT `fk_books_publishers1`
  FOREIGN KEY (`publisher_id`)
  REFERENCES `mydb`.`publishers` (`id`)
  ON DELETE SET NULL
  ON UPDATE NO ACTION;
