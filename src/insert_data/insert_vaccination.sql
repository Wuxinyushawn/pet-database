-- 05_insert_vaccination.sql
-- Source: Vaccination.csv

INSERT INTO vaccination (
    vaccination_id,
    pet_id,
    vaccine_name,
    dose_no,
    vaccination_date,
    next_due_date,
    vet_name,
    notes
) VALUES
(1, 3, 'Rabies', 1, '2025-05-24', '2026-04-22', 'Dr. Williams', 'Given successfully'),
(2, 8, 'Rabies', 3, '2025-10-28', '2026-04-03', 'Dr. Johnson', 'Up to date'),
(3, 15, 'Myxomatosis', 3, '2025-11-22', '2026-04-25', 'Dr. Brown', 'Regular schedule'),
(4, 19, 'Rabies', 3, '2025-12-17', '2026-05-14', 'Dr. Smith', 'Booster needed'),
(5, 7, 'Myxomatosis', 3, '2025-05-06', '2026-03-01', 'Dr. Johnson', 'Booster needed'),
(6, 18, 'Rabies', 1, '2025-04-16', '2026-04-02', 'Dr. Brown', 'Up to date'),
(7, 10, 'Psittacine Pasteurella Vaccine', 1, '2025-06-28', '2026-05-10', 'Dr. Williams', 'Up to date'),
(8, 3, 'Distemper', 2, '2025-11-03', '2026-04-30', 'Dr. Johnson', 'Up to date'),
(9, 4, 'Distemper', 3, '2025-05-24', '2026-03-15', 'Dr. Johnson', 'Given successfully'),
(10, 2, 'Psittacine Pasteurella Vaccine', 2, '2025-09-15', '2026-05-15', 'Dr. Williams', 'Up to date'),
(11, 4, 'Feline Leukemia', 3, '2025-07-02', '2026-05-09', 'Dr. Brown', 'Regular schedule'),
(12, 17, 'Psittacine Pasteurella Vaccine', 2, '2025-05-06', '2026-04-26', 'Dr. Smith', 'Up to date'),
(13, 11, 'Myxomatosis', 1, '2025-05-09', '2026-03-10', 'Dr. Smith', 'Regular schedule'),
(14, 19, 'Rabies', 1, '2025-08-14', '2026-04-16', 'Dr. Brown', 'Regular schedule'),
(15, 6, 'Parvo', 3, '2025-11-10', '2026-04-12', 'Dr. Smith', 'Up to date'),
(16, 12, 'Parvo', 2, '2025-07-07', '2026-05-05', 'Dr. Smith', 'Booster needed'),
(17, 11, 'Myxomatosis', 3, '2025-08-20', '2026-03-17', 'Dr. Brown', 'Given successfully'),
(18, 15, 'Myxomatosis', 2, '2025-06-19', '2026-03-22', 'Dr. Smith', 'Up to date'),
(19, 17, 'Avian Pox Vaccine', 3, '2025-11-24', '2026-04-19', 'Dr. Brown', 'Up to date'),
(20, 2, 'Avian Pox Vaccine', 3, '2025-07-17', '2026-04-29', 'Dr. Brown', 'Up to date');