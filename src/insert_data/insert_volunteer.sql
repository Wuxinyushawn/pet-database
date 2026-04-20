-- 03_insert_volunteer.sql
-- Source: Volunteer.csv

INSERT INTO volunteer (
    volunteer_id,
    shelter_id,
    full_name,
    phone,
    email,
    join_date,
    availability_note
) VALUES
(1, 1, 'Mark Evans', '213-555-2001', 'mark.evans@example.com', '2025-06-07', 'Weekdays'),
(2, 1, 'Sophia Green', '213-555-2002', 'sophia.green@example.com', '2025-05-19', 'Weekdays'),
(3, 2, 'Daniel King', '212-555-2003', 'daniel.king@example.com', '2025-09-14', 'Flexible'),
(4, 3, 'Olivia Wright', '212-555-2004', 'olivia.wright@example.com', '2025-04-23', 'Evenings'),
(5, 1, 'Ethan Scott', '312-555-2005', 'ethan.scott@example.com', '2025-04-27', 'Weekdays'),
(6, 1, 'Mia Lopez', '312-555-2006', 'mia.lopez@example.com', '2025-04-19', 'Flexible'),
(7, 3, 'Lucas Hill', '213-555-2007', 'lucas.hill@example.com', '2025-06-12', 'Weekends only'),
(8, 2, 'Amelia Perez', '212-555-2008', 'amelia.perez@example.com', '2025-05-16', 'Evenings'),
(9, 1, 'Benjamin Carter', '312-555-2009', 'benjamin.carter@example.com', '2025-04-19', 'Weekdays'),
(10, 2, 'Charlotte Murphy', '213-555-2010', 'charlotte.murphy@example.com', '2025-10-01', 'Weekdays');