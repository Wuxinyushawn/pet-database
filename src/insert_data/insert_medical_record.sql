-- 06_insert_medical_record.sql
-- Source: MedicalRecord.csv

INSERT INTO medical_record (
    record_id,
    pet_id,
    visit_date,
    record_type,
    diagnosis,
    treatment,
    vet_name,
    notes
) VALUES
(1, 5, '2026-01-14', 'Check-up', 'Routine check', 'Medication', 'Dr. Smith', 'Good condition'),
(2, 5, '2025-12-08', 'Treatment', 'Healthy', 'Surgery', 'Dr. Brown', 'Follow up needed'),
(3, 7, '2025-12-04', 'Surgery', 'Cold', NULL, 'Dr. Williams', 'Good condition'),
(4, 9, '2025-05-27', 'Treatment', 'Healthy', 'Medication', 'Dr. Williams', 'Recovering well'),
(5, 3, '2025-05-06', 'Check-up', 'Minor injury', 'Rest', 'Dr. Smith', 'Recovering well'),
(6, 8, '2025-06-19', 'Check-up', 'Healthy', 'Rest', 'Dr. Brown', 'Follow up needed'),
(7, 12, '2025-07-10', 'Check-up', 'Minor injury', 'Surgery', 'Dr. Smith', 'Regular checkup'),
(8, 10, '2026-02-04', 'Check-up', 'Routine check', 'Rest', 'Dr. Smith', 'Recovering well'),
(9, 4, '2025-09-17', 'Check-up', 'Healthy', 'Surgery', 'Dr. Brown', 'Follow up needed'),
(10, 3, '2025-12-31', 'Surgery', 'Healthy', NULL, 'Dr. Brown', 'Regular checkup'),
(11, 14, '2025-10-18', 'Check-up', 'Minor injury', NULL, 'Dr. Johnson', 'Follow up needed'),
(12, 20, '2026-01-16', 'Check-up', 'Routine check', NULL, 'Dr. Williams', 'Follow up needed'),
(13, 8, '2025-05-30', 'Surgery', 'Routine check', 'Rest', 'Dr. Brown', 'Good condition'),
(14, 11, '2025-04-30', 'Treatment', 'Cold', 'Rest', 'Dr. Brown', 'Recovering well'),
(15, 12, '2025-08-26', 'Surgery', 'Cold', 'Surgery', 'Dr. Smith', 'Recovering well'),
(16, 3, '2025-08-17', 'Check-up', 'Routine check', 'Rest', 'Dr. Brown', 'Good condition'),
(17, 15, '2025-04-24', 'Check-up', 'Cold', 'Rest', 'Dr. Brown', 'Recovering well'),
(18, 10, '2026-02-07', 'Surgery', 'Routine check', 'Surgery', 'Dr. Brown', 'Follow up needed'),
(19, 12, '2025-12-04', 'Surgery', 'Cold', 'Surgery', 'Dr. Johnson', 'Regular checkup'),
(20, 7, '2025-09-24', 'Check-up', 'Minor injury', 'Rest', 'Dr. Johnson', 'Good condition'),
(21, 9, '2026-01-09', 'Surgery', 'Healthy', 'Rest', 'Dr. Williams', 'Recovering well'),
(22, 12, '2025-07-16', 'Surgery', 'Healthy', 'Rest', 'Dr. Williams', 'Regular checkup'),
(23, 2, '2026-01-24', 'Surgery', 'Minor injury', NULL, 'Dr. Smith', 'Regular checkup'),
(24, 19, '2025-09-08', 'Check-up', 'Routine check', NULL, 'Dr. Williams', 'Recovering well'),
(25, 2, '2025-08-23', 'Treatment', 'Healthy', 'Medication', 'Dr. Brown', 'Good condition');