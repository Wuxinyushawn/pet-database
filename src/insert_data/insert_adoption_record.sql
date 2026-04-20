-- 09_insert_adoption_record.sql
-- Source: AdoptionRecord.csv

INSERT INTO adoption_record (
    adoption_id,
    application_id,
    adoption_date,
    final_adoption_fee,
    handover_note
) VALUES
(1, 3, '2025-09-13', 137.09, 'All paperwork signed'),
(2, 4, '2025-10-10', 66.26, 'Vaccines up to date'),
(3, 6, '2025-09-01', 159.28, 'All paperwork signed'),
(4, 10, '2025-11-28', 140.93, 'Completed'),
(5, 14, '2025-10-01', 127.99, 'Home check done'),
(6, 15, '2025-10-22', 56.66, 'Vaccines up to date');