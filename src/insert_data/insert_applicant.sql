-- 02_insert_applicant.sql
-- Source: Applicant.csv

INSERT INTO applicant (
    applicant_id,
    full_name,
    phone,
    email,
    address,
    housing_type,
    has_pet_experience,
    created_at
) VALUES
(1, 'James Wilson', '310-555-1001', 'james.wilson@example.com', '123 Oak St, LA', 'Apartment', 0, '2025-07-15'),
(2, 'Emily Davis', '310-555-1002', 'emily.davis@example.com', '456 Pine St, NY', 'Condo', 0, '2025-08-13'),
(3, 'Michael Brown', '310-555-1003', 'michael.brown@example.com', '789 Maple St, TX', 'Apartment', 1, '2025-05-01'),
(4, 'Sarah Taylor', '310-555-1004', 'sarah.taylor@example.com', '101 Cedar Ave, CA', 'Condo', 0, '2025-05-13'),
(5, 'David Clark', '310-555-1005', 'david.clark@example.com', '234 Birch Rd, FL', 'House', 1, '2025-06-03'),
(6, 'Jennifer Lewis', '310-555-1006', 'jennifer.lewis@example.com', '567 Palm Dr, AZ', 'Condo', 1, '2025-08-02'),
(7, 'Robert Walker', '310-555-1007', 'robert.walker@example.com', '890 Spruce Ln, WA', 'House', 0, '2025-08-12'),
(8, 'Lisa Hall', '310-555-1008', 'lisa.hall@example.com', '112 Willow Ct, OR', 'House', 1, '2025-08-07'),
(9, 'Thomas Allen', '310-555-1009', 'thomas.allen@example.com', '223 Aspen Pl, NV', 'Apartment', 1, '2025-08-30'),
(10, 'Amanda Young', '310-555-1010', 'amanda.young@example.com', '334 Cherry St, CO', 'Apartment', 1, '2025-05-31'),
(11, 'William King', '310-555-1011', 'william.king@example.com', '445 Peach St, MA', 'House', 1, '2025-07-29'),
(12, 'Chloe Scott', '310-555-1012', 'chloe.scott@example.com', '556 Berry Ave, NJ', 'Condo', 0, '2025-05-09'),
(13, 'Richard Green', '310-555-1013', 'richard.green@example.com', '667 Nut St, CT', 'Condo', 1, '2025-05-28'),
(14, 'Elizabeth Baker', '310-555-1014', 'elizabeth.baker@example.com', '778 Seed Ct, MD', 'Condo', 1, '2025-07-09'),
(15, 'Joseph Adams', '310-555-1015', 'joseph.adams@example.com', '889 Leaf Rd, VA', 'Townhouse', 0, '2025-06-28');