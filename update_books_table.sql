USE mydb;

-- First, let's see what foreign keys exist
SELECT CONSTRAINT_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'mydb' 
AND TABLE_NAME = 'books'
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Make author_id nullable (this should work regardless of constraints)
ALTER TABLE books 
MODIFY COLUMN author_id INT NULL;

-- Now try to drop the foreign key if it exists
SET @constraint_name = (
    SELECT CONSTRAINT_NAME 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = 'mydb' 
    AND TABLE_NAME = 'books' 
    AND COLUMN_NAME = 'author_id' 
    AND REFERENCED_TABLE_NAME IS NOT NULL
);

SET @sql = IF(@constraint_name IS NOT NULL,
    CONCAT('ALTER TABLE books DROP FOREIGN KEY ', @constraint_name),
    'SELECT "No foreign key constraint found on author_id"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Finally, drop the column
ALTER TABLE books 
DROP COLUMN author_id;
