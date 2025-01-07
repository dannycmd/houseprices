-- DROP DATABASE IF EXISTS `houseprices`;
-- CREATE DATABASE `houseprices`;
USE `houseprices`;

CREATE TABLE `pricepaid` (
    `unique_id` VARCHAR(100),
    `price_paid` DECIMAL,
    `deed_date` DATE,
    `postcode` VARCHAR(8),
    `property_type` VARCHAR(1),
    `new_build` VARCHAR(1),
    `estate_type` VARCHAR(1),
    `saon` VARCHAR(50),
    `paon` VARCHAR(50),
    `street` VARCHAR(50),
    `locality` VARCHAR(50),
    `town` VARCHAR(50),
    `district` VARCHAR(50),
    `county` VARCHAR(50),
    `transaction_category` VARCHAR(1),
    `linked_data_uri` VARCHAR(1),
    PRIMARY KEY (unique_id)
);

SET GLOBAL local_infile=ON;

-- had to add OPT_LOCAL_INFILE=1 to Connection -> Advanced -> Others for query below to run

mysql --local-infile=1 -u root -p
SET autocommit=0;
SET unique_checks=1;
SET foreign_key_checks=0;

LOAD DATA LOW_PRIORITY LOCAL INFILE 'C:/Users/danjr/Documents/Projects/UK House Prices Visualisation/pricepaid.csv' INTO TABLE pricepaid 
CHARACTER SET armscii8 FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' 
(`unique_id`,`price_paid`,`deed_date`,`postcode`,`property_type`,`new_build`,`estate_type`,`saon`,`paon`,`street`,`locality`,`town`,`district`,`county`,`transaction_category`,`linked_data_uri`);

-- CREATE INDEX idx_lastname
-- ON Persons (LastName);



--columns=unique_id,price_paid,deed_date,postcode,property_type,new_build,estate_type,saon,paon,street,locality,town,district,county,transaction_category,linked_data_uri