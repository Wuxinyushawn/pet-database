-- 04_insert_pet.sql
-- Source: Pet.csv

INSERT INTO pet (
    pet_id,
    shelter_id,
    name,
    species,
    breed,
    sex,
    color,
    estimated_birth_date,
    intake_date,
    status,
    is_sterilized,
    special_needs
) VALUES
(1, 1, 'Luna', 'Dog', 'Labrador', 'Male', 'Brown', '2021-03-22', '2025-04-27', 'available', 1, NULL),
(2, 1, 'Milo', 'Bird', 'Parakeet', 'Male', 'Black', '2021-11-13', '2025-07-17', 'adopted', 1, 'Behavioral training'),
(3, 1, 'Bella', 'Cat', 'Bengal', 'Female', 'Golden', '2023-02-09', '2025-05-06', 'adopted', 1, 'Special diet'),
(4, 1, 'Charlie', 'Cat', 'Maine Coon', 'Female', 'Black', '2023-02-01', '2025-05-24', 'available', 0, NULL),
(5, 3, 'Daisy', 'Bird', 'Lovebird', 'Female', 'Black', '2021-06-28', '2025-10-18', 'available', 1, 'Special diet'),
(6, 1, 'Max', 'Dog', 'Labrador', 'Male', 'White', '2022-11-19', '2025-09-05', 'adopted', 1, 'Behavioral training'),
(7, 3, 'Lucy', 'Rabbit', 'Dutch', 'Female', 'Brown', '2021-03-08', '2025-05-06', 'medical_hold', 1, 'Special diet'),
(8, 3, 'Cooper', 'Cat', 'Siamese', 'Male', 'Gray', '2023-03-13', '2025-05-14', 'adopted', 0, 'Special diet'),
(9, 1, 'Chloe', 'Dog', 'Poodle', 'Female', 'Gray', '2023-10-28', '2025-05-27', 'medical_hold', 1, 'Behavioral training'),
(10, 3, 'Lily', 'Bird', 'Parakeet', 'Female', 'Brown', '2021-09-26', '2025-06-28', 'available', 1, 'Behavioral training'),
(11, 1, 'Oliver', 'Rabbit', 'Dutch', 'Male', 'White', '2024-02-27', '2025-04-30', 'available', 1, 'Behavioral training'),
(12, 3, 'Sadie', 'Dog', 'Bulldog', 'Male', 'Gray', '2021-03-14', '2025-06-13', 'available', 0, 'Medication'),
(13, 2, 'Rocky', 'Rabbit', 'Dutch', 'Male', 'Brown', '2023-07-16', '2025-12-28', 'available', 1, 'Special diet'),
(14, 1, 'Zoe', 'Dog', 'Poodle', 'Male', 'Golden', '2021-12-28', '2025-05-23', 'adopted', 1, NULL),
(15, 2, 'Teddy', 'Rabbit', 'Lionhead', 'Male', 'Black', '2024-09-09', '2025-04-19', 'adopted', 0, NULL),
(16, 3, 'Molly', 'Dog', 'Bulldog', 'Female', 'Black', '2021-12-07', '2025-06-22', 'available', 1, 'Medication'),
(17, 2, 'Duke', 'Bird', 'Parakeet', 'Female', 'Golden', '2022-07-23', '2025-05-06', 'available', 0, 'Behavioral training'),
(18, 1, 'Nala', 'Dog', 'German Shepherd', 'Male', 'White', '2021-09-18', '2025-04-16', 'reserved', 0, NULL),
(19, 2, 'Oscar', 'Dog', 'Labrador', 'Male', 'White', '2022-02-18', '2025-08-14', 'available', 1, 'Medication'),
(20, 1, 'Bailey', 'Bird', 'Parakeet', 'Female', 'Golden', '2022-09-25', '2025-07-22', 'available', 0, NULL);