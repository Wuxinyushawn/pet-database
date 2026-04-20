-- 10_insert_follow_up.sql
-- Source: FollowUp.csv

INSERT INTO follow_up (
    followup_id,
    adoption_id,
    followup_date,
    followup_type,
    pet_condition,
    adopter_feedback,
    result_status,
    staff_note
) VALUES
(1, 1, '2025-09-27', 'Phone Check', 'Stable', 'Great companion', 'Good', 'Good progress'),
(2, 1, '2026-02-16', 'Home Visit', 'Improving', 'Loving pet', 'Good', 'All good'),
(3, 1, '2026-01-04', 'Vet Check', 'Stable', 'Great companion', 'Good', 'All good'),
(4, 2, '2025-10-18', 'Home Visit', 'Improving', 'Loving pet', 'Excellent', 'Regular check needed'),
(5, 2, '2025-12-29', 'Phone Check', 'Good', 'Good adjustment', 'Excellent', 'Pet doing well'),
(6, 2, '2025-11-26', 'Vet Check', 'Healthy', 'Great companion', 'Needs Improvement', 'Regular check needed'),
(7, 3, '2026-02-05', 'Vet Check', 'Stable', 'Good adjustment', 'Good', 'Pet doing well'),
(8, 3, '2025-09-16', 'Vet Check', 'Good', 'Good adjustment', 'Needs Improvement', 'Pet doing well'),
(9, 3, '2025-11-28', 'Home Visit', 'Stable', 'Good adjustment', 'Needs Improvement', 'Good progress'),
(10, 4, '2026-04-08', 'Vet Check', 'Stable', 'Good adjustment', 'Needs Improvement', 'All good'),
(11, 4, '2025-12-03', 'Phone Check', 'Improving', 'Great companion', 'Good', 'Good progress'),
(12, 5, '2025-11-13', 'Vet Check', 'Good', 'Loving pet', 'Needs Improvement', 'All good'),
(13, 5, '2025-10-15', 'Vet Check', 'Improving', 'Great companion', 'Good', 'All good'),
(14, 6, '2025-11-10', 'Home Visit', 'Stable', 'Great companion', 'Satisfactory', 'All good'),
(15, 6, '2026-02-21', 'Home Visit', 'Good', 'Great companion', 'Needs Improvement', 'Pet doing well'),
(16, 6, '2026-02-03', 'Vet Check', 'Healthy', 'Loving pet', 'Satisfactory', 'All good');