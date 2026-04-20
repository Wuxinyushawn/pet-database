-- 01_insert_shelter.sql
-- Source: Shelter.csv

INSERT INTO shelter (
    shelter_id,
    name,
    address,
    phone,
    capacity
) VALUES
(1, 'Happy Paws Shelter', '123 Main St, City A', '123-456-7890', 50),
(2, 'Pet Haven', '456 Oak Ave, City B', '234-567-8901', 30),
(3, 'Animal Rescue Center', '789 Pine Rd, City C', '345-678-9012', 40);