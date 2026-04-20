-- =========================================
-- indexing.sql
-- Representative indexes for the
-- animal shelter management database
-- =========================================

-- Note:
-- Primary keys are already indexed automatically.
-- The following indexes are selected to represent
-- the most important foreign-key, filtering, and
-- reporting use cases in this system.

-- 1. Foreign key index for shelter-pet relationship
-- Used in joins and shelter-based pet lookup
CREATE INDEX idx_pet_shelter_id
ON PET(shelter_id);

-- 2. Status index for operational pet filtering
-- Used to find available / reserved / medical-hold pets
CREATE INDEX idx_pet_status
ON PET(status);

-- 3. Intake date index for long-stay pet analysis
-- Used in time-based reports and ordering
CREATE INDEX idx_pet_intake_date
ON PET(intake_date);

-- 4. Foreign key index for vaccination-pet relationship
-- Used to retrieve vaccination history of a pet
CREATE INDEX idx_vaccination_pet_id
ON VACCINATION(pet_id);

-- 5. Due date index for vaccination reminders
-- Used to identify vaccinations due soon
CREATE INDEX idx_vaccination_next_due_date
ON VACCINATION(next_due_date);

-- 6. Foreign key index for adoption application by applicant
-- Used in applicant-application joins
CREATE INDEX idx_adoption_application_applicant_id
ON ADOPTION_APPLICATION(applicant_id);

-- 7. Status index for adoption application workflow
-- Used to filter under-review / approved / rejected cases
CREATE INDEX idx_adoption_application_status
ON ADOPTION_APPLICATION(status);

-- 8. Foreign key index for volunteer assignments
-- Used in volunteer task lookup
CREATE INDEX idx_care_assignment_volunteer_id
ON CARE_ASSIGNMENT(volunteer_id);

-- 9. Composite index for volunteer schedule queries
-- Used when checking one volunteer's assignments by date
CREATE INDEX idx_care_assignment_volunteer_date
ON CARE_ASSIGNMENT(volunteer_id, assignment_date);

-- 10. Foreign key index for follow-up records
-- Used to retrieve all follow-up records for one adoption
CREATE INDEX idx_follow_up_adoption_id
ON FOLLOW_UP(adoption_id);