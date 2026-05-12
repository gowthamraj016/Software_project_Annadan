# SPRINT 2 REPORT
## AnnaDaan - Smart Food Donation Management System

---

## Sprint Overview

| **Attribute** | **Details** |
|---------------|-------------|
| **Sprint Number** | Sprint 2 |
| **Sprint Goal** | Donation Workflow |
| **Sprint Duration** | April 1, 2026 - April 14, 2026 (10 working days) |
| **Total Story Points** | 23 points |
| **Story Points Completed** | 23 points (100%) |
| **Total Tasks** | 23 tasks |
| **Total Estimated Hours** | 72 hours |

---

## Team Information

| **Role** | **Name** | **Responsibilities** |
|----------|----------|---------------------|
| **Product Owner** | K. Mani Vignesh | Sprint planning, backlog prioritization, stakeholder communication |
| **Scrum Master** | M. Manish Kumar Reddy | Facilitation, impediment removal, process adherence |
| **Developer** | D. Naga Gowtham Raj | Development, testing, UI/UX implementation |

---

## User Stories Completed

### STORY-5: Create Food Donation Listing (8 points)
**As a donor, I want to create a food donation listing so that receivers can request it**

**Acceptance Criteria:**
- Donation form with all required fields
- Map integration for location selection
- Geocoding for address lookup
- Image upload for food items
- Expiry date validation

**Tasks Completed:**
- Design donation form UI
- Integrate Leaflet.js map for location
- Implement Nominatim geocoding API
- Create Donation model with all fields
- Implement form validation logic
- Write test case TC_S2_01
- Create donation creation view

**Status:** ✅ Completed

---

### STORY-6: View Donation Status (5 points)
**As a donor, I want to view my donation status so that I can track them**

**Acceptance Criteria:**
- List all donations by donor
- Filter by status (Available, Requested, Accepted, Completed)
- Search functionality
- Display food saved statistics

**Tasks Completed:**
- Design donations list UI
- Implement status filtering logic
- Add search functionality
- Calculate food saved statistics
- Create my_donations view

**Status:** ✅ Completed

---

### STORY-7: Request Food Donation (5 points)
**As a receiver, I want to request food so that I can receive donations**

**Acceptance Criteria:**
- Browse available donations
- Submit request with reason
- Email notification to donor
- Prevent duplicate requests

**Tasks Completed:**
- Design request form UI
- Create DonationRequest model
- Implement request creation logic
- Add email notification system
- Prevent duplicate requests

**Status:** ✅ Completed

---

### STORY-8: Accept Donation Request (5 points)
**As a donor, I want to accept one request so that I can schedule pickup**

**Acceptance Criteria:**
- View all requests for donation
- Accept one request
- Auto-reject other pending requests
- Schedule pickup time
- Send acceptance notifications

**Tasks Completed:**
- Design request management UI
- Implement accept/reject logic
- Add pickup scheduling form
- Auto-reject other pending requests
- Send acceptance notifications
- Create Pickup model

**Status:** ✅ Completed

---

## Sprint Metrics

### Velocity
- **Planned Velocity:** 23 story points
- **Actual Velocity:** 23 story points
- **Velocity Achievement:** 100%

### Burndown Analysis
- **Day 1-2:** Donation form and model setup (3 hours)
- **Day 3-5:** Map integration and geocoding (16 hours)
- **Day 6-7:** Donation listing and filtering (17 hours)
- **Day 8-9:** Request management system (14 hours)
- **Day 10-12:** Accept/reject workflow and pickup (22 hours)
- **Sprint completed by Day 12** with all 23 points delivered

### Task Completion
- **Total Tasks:** 23
- **Completed Tasks:** 23
- **Completion Rate:** 100%

---

## Technical Achievements

### Technologies Implemented
- **Backend:** Django models (Donation, DonationRequest, Pickup)
- **Frontend:** Leaflet.js for interactive maps, Tailwind CSS
- **APIs:** Nominatim Geocoding API for address lookup
- **Email:** SMTP notifications for requests and acceptances
- **Database:** SQLite with foreign key relationships

### Key Features Delivered
1. ✅ Complete donation creation with map-based location selection
2. ✅ Donation listing with search and filter capabilities
3. ✅ Request management system with email notifications
4. ✅ Accept/reject workflow with automatic request handling
5. ✅ Pickup scheduling functionality

### Test Coverage
- **Test Case TC_S2_01:** Donation Creation Flow - ✅ PASS
- **Manual Testing:** Request submission, Accept workflow - ✅ PASS

---

## Sprint Review

### Date & Time
**April 14, 2026 | 10:00 AM - 3:00 PM**

### Attendees
- K. Mani Vignesh (Product Owner)
- M. Manish Kumar Reddy (Scrum Master)
- D. Naga Gowtham Raj (Developer)
- Stakeholders

### Demonstration
✅ Donation creation with interactive map  
✅ Donation listing with filters  
✅ Request submission workflow  
✅ Accept request with pickup scheduling  

### Stakeholder Feedback
- **Positive:** Excellent map integration, intuitive workflow
- **Suggestions:** Add bulk donation support in future
- **Concerns:** None

### Key Decisions
1. ✅ All sprint deliverables completed successfully
2. ✅ Donation workflow foundation ready for Sprint 3
3. ✅ Proceed with AI prioritization in next sprint
4. ✅ Map integration exceeded expectations

---

## Sprint Retrospective

### Date & Time
**April 14, 2026 | 3:00 PM - 5:00 PM**

### Attendees
- K. Mani Vignesh (Product Owner)
- M. Manish Kumar Reddy (Scrum Master)
- D. Naga Gowtham Raj (Developer)

### What Went Well ✅
1. **Map Integration:** Leaflet.js implementation smooth and effective
2. **Task Coordination:** Better task allocation than Sprint 1
3. **Email System:** Notification system working reliably
4. **Code Quality:** Improved with peer reviews
5. **Sprint Planning:** More accurate estimations

### What Could Be Improved 🔄
1. **API Documentation:** Need better Nominatim API documentation
2. **Testing Coverage:** Increase automated tests
3. **Communication:** More frequent check-ins during complex tasks
4. **Code Refactoring:** Some duplicate code needs cleanup
5. **Performance:** Optimize map loading time

### Action Items for Sprint 3
| **Action Item** | **Owner** | **Priority** |
|-----------------|-----------|--------------|
| Increase team coordination and communication | All Team | High |
| Optimize map loading performance | Gowtham Raj | High |
| Add comprehensive API documentation | Manish Kumar | Medium |
| Refactor duplicate code | Mani Vignesh | Medium |
| Increase automated test coverage | Manish Kumar | Medium |

### Team Morale
**Rating:** 9.5/10 - Excellent progress and team synergy

---

## Deployment Status

### Staging Environment
- **Deployed:** April 14, 2026 at 5:00 PM
- **Status:** ✅ Successful
- **Smoke Tests:** ✅ All Passed
- **URL:** staging.annadaan.local

### Production Environment
- **Status:** Not deployed (waiting for Sprint 4 completion)

---

## Risks & Issues

### Risks Identified
- None

### Issues Encountered
- **Issue #1:** Leaflet.js documentation unclear initially
  - **Resolution:** Found community examples and tutorials
  - **Status:** ✅ Resolved
  
- **Issue #2:** SMTP configuration for notifications
  - **Resolution:** Configured timeout and retry settings
  - **Status:** ✅ Resolved

---

## Sprint Artifacts

### Documents Created
1. ✅ Product Backlog (01_product_backlog.csv/html)
2. ✅ Sprint Backlog (02_sprint_backlog.csv/html)
3. ✅ Daily Scrum Week 1 (03_daily_scrum_week1.csv/html)
4. ✅ Daily Scrum Week 2 (03_daily_scrum_week2.csv/html)
5. ✅ Deployment Plan (04_deployment_plan.csv/html)
6. ✅ Burndown Chart (05_burndown_chart.csv/html)

### Code Repositories
- **Branch:** sprint-2-donation-workflow
- **Commits:** 53 commits
- **Lines of Code:** ~3,200 lines

---

## Next Sprint Preview

### Sprint 3 Goals
- Implement AI-based request prioritization
- Add pickup tracking system
- Create pickup completion workflow
- Build admin pickup dashboard

### Estimated Story Points
- 23 points (STORY-9, STORY-10, STORY-11, STORY-12)

---

## Sign-off

| **Role** | **Name** | **Signature** | **Date** |
|----------|----------|---------------|----------|
| **Product Owner** | K. Mani Vignesh | _______________ | April 14, 2026 |
| **Scrum Master** | M. Manish Kumar Reddy | _______________ | April 14, 2026 |
| **Developer** | D. Naga Gowtham Raj | _______________ | April 14, 2026 |

---

**Report Generated:** April 14, 2026  
**Sprint Status:** ✅ COMPLETED SUCCESSFULLY  
**Next Sprint Start:** April 15, 2026
