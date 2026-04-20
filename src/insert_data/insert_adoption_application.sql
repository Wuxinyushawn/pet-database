-- 08_insert_adoption_application.sql
-- Source: AdoptionApplication.csv

INSERT INTO adoption_application (
    application_id,
    applicant_id,
    pet_id,
    application_date,
    status,
    reason,
    reviewed_date,
    reviewer_name,
    decision_note
) VALUES
(1, 7, 18, '2025-10-11', 'Under Review', 'Love animals', NULL, 'Hannah Brooks', NULL),
(2, 12, 18, '2025-05-10', 'Rejected', 'Family companion', '2025-05-20', 'Hannah Brooks', 'Rejected due to fit'),
(3, 9, 3, '2025-09-05', 'Approved', 'Family companion', '2025-09-10', 'Hannah Brooks', 'Approved - suitable home'),
(4, 10, 2, '2025-09-30', 'Approved', 'Looking for pet', '2025-10-05', 'Hannah Brooks', 'Approved - suitable home'),
(5, 12, 11, '2025-06-25', 'Rejected', 'Looking for pet', '2025-07-12', 'Hannah Brooks', 'Rejected due to fit'),
(6, 1, 15, '2025-08-01', 'Approved', 'Family companion', '2025-08-10', 'Marcus Reed', 'Approved'),
(7, 15, 8, '2025-07-28', 'Rejected', 'Love animals', '2025-10-16', 'Priya Nair', 'Rejected due to fit'),
(8, 14, 18, '2025-07-10', 'Under Review', 'Love animals', NULL, 'Hannah Brooks', NULL),
(9, 5, 20, '2025-07-25', 'Rejected', 'Love animals', '2025-09-27', 'Hannah Brooks', 'Rejected due to fit'),
(10, 2, 14, '2025-11-23', 'Approved', 'Family companion', '2025-11-25', 'Hannah Brooks', 'Approved - suitable home'),
(11, 8, 18, '2025-10-22', 'Under Review', 'Family companion', NULL, 'Hannah Brooks', NULL),
(12, 10, 18, '2025-06-01', 'Rejected', 'Love animals', '2025-06-10', 'Hannah Brooks', 'Rejected due to housing'),
(13, 11, 8, '2025-10-12', 'Rejected', 'Child friendly', '2025-10-22', 'Priya Nair', 'Rejected due to housing'),
(14, 14, 6, '2025-09-15', 'Approved', 'Looking for pet', '2025-09-22', 'Hannah Brooks', 'Good candidate'),
(15, 13, 8, '2025-07-02', 'Approved', 'Family companion', '2025-07-08', 'Priya Nair', 'Approved - suitable home');