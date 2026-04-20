-- 07_insert_care_assignment.sql
-- Source: CareAssignment.csv

INSERT INTO CARE_ASSIGNMENT (assignment_id, volunteer_id, pet_id, assignment_date, shift, task_type, status, notes) VALUES
(1, 7, 16, '2025-08-14', 'Morning', 'Cleaning', 'Cancelled', 'Special attention needed'),
(2, 7, 7, '2025-09-16', 'Afternoon', 'Walking', 'Completed', 'Handled well'),
(3, 9, 12, '2025-08-20', 'Evening', 'Feeding', 'Pending', 'Needs monitoring'),
(4, 2, 5, '2025-09-01', 'Morning', 'Medication', 'Completed', 'Given on time'),
(5, 1, 3, '2025-09-05', 'Afternoon', 'Walking', 'Completed', 'Friendly with staff'),
(6, 4, 8, '2025-09-10', 'Evening', 'Cleaning', 'Pending', 'Kennel area only'),
(7, 5, 1, '2025-09-12', 'Morning', 'Feeding', 'Completed', 'Ate all food'),
(8, 6, 6, '2025-09-13', 'Afternoon', 'Exercise', 'Completed', 'Very active'),
(9, 8, 10, '2025-09-14', 'Morning', 'Medical Transport', 'Pending', 'Vet visit tomorrow'),
(10, 3, 14, '2025-09-15', 'Evening', 'Walking', 'Cancelled', 'Bad weather'),
(11, 10, 18, '2025-09-16', 'Morning', 'Medication', 'Completed', 'Applied cream'),
(12, 2, 11, '2025-09-17', 'Afternoon', 'Grooming', 'Pending', 'Sensitive skin'),
(13, 1, 9, '2025-09-18', 'Evening', 'Feeding', 'Completed', 'Calm behavior'),
(14, 4, 15, '2025-09-19', 'Morning', 'Cleaning', 'Completed', 'Litter replaced'),
(15, 6, 20, '2025-09-20', 'Afternoon', 'Health Check Support', 'Pending', 'Needs follow-up');