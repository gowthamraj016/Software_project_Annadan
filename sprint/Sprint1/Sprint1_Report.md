# SPRINT 1 REPORT
## AnnaDaan - Smart Food Donation Management System

---

## Sprint Overview

| **Attribute** | **Details** |
|---------------|-------------|
| **Sprint Number** | Sprint 1 |
| **Sprint Goal** | Authentication & User Management |
| **Sprint Duration** | March 18, 2026 - March 31, 2026 (10 working days) |
| **Total Story Points** | 23 points |
| **Story Points Completed** | 23 points (100%) |
| **Total Tasks** | 22 tasks |
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

### STORY-1: User Registration (8 points)
**As a user, I want to register an account so that I can access the platform**

**Acceptance Criteria:**
- User can register as Donor or Receiver
- Email verification implemented
- Password strength validation
- Profile creation with required fields

**Tasks Completed:**
- Design registration form UI
- Implement user model (Donor, Receiver, Admin)
- Add email verification system
- Create password validation logic
- Implement profile creation flow
- Write test case TC_S1_01

**Status:** ✅ Completed

---

### STORY-2: User Login (5 points)
**As a user, I want to log in to my account so that I can use the platform features**

**Acceptance Criteria:**
- Secure login with email/password
- Session management
- Remember me functionality
- Error handling for invalid credentials

**Tasks Completed:**
- Design login page UI
- Implement Django authentication
- Add session management
- Create remember me functionality
- Implement error handling

**Status:** ✅ Completed

---

### STORY-3: Profile Management (5 points)
**As a user, I want to manage my profile so that I can keep my information updated**

**Acceptance Criteria:**
- View profile information
- Edit profile details
- Upload profile picture
- Update contact information

**Tasks Completed:**
- Design profile page UI
- Implement profile view
- Add profile edit functionality
- Implement image upload
- Create profile update logic

**Status:** ✅ Completed

---

### STORY-4: Password Reset (5 points)
**As a user, I want to reset my password so that I can recover my account**

**Acceptance Criteria:**
- Forgot password functionality
- Email-based password reset
- Secure token generation
- Password change confirmation

**Tasks Completed:**
- Design password reset UI
- Implement forgot password flow
- Add email token generation
- Create password reset view
- Send password reset emails
- Write password reset tests

**Status:** ✅ Completed

---

## Sprint Metrics

### Velocity
- **Planned Velocity:** 23 story points
- **Actual Velocity:** 23 story points
- **Velocity Achievement:** 100%

### Burndown Analysis
- **Day 1-2:** Initial setup and planning (6 hours)
- **Day 3-5:** Core authentication implementation (18 hours)
- **Day 6-8:** Profile management and password reset (21 hours)
- **Day 9-10:** Testing and bug fixes (27 hours)
- **Sprint completed by Day 10** with all 23 points delivered

### Task Completion
- **Total Tasks:** 22
- **Completed Tasks:** 22
- **Completion Rate:** 100%

---

## Technical Achievements

### Technologies Implemented
- **Backend:** Django 4.2, Django Authentication System
- **Frontend:** HTML5, Tailwind CSS, JavaScript
- **Database:** SQLite with User, Donor, Receiver, Admin models
- **Email:** SMTP configuration for verification and password reset
- **Security:** Password hashing, CSRF protection, session management

### Key Features Delivered
1. ✅ Complete user registration system with email verification
2. ✅ Secure login with session management
3. ✅ Profile management with image upload
4. ✅ Password reset via email
5. ✅ Role-based access (Donor, Receiver, Admin)

### Test Coverage
- **Test Case TC_S1_01:** User Registration Flow - ✅ PASS
- **Manual Testing:** Login, Profile Edit, Password Reset - ✅ PASS

---

## Sprint Review

### Date & Time
**March 31, 2026 | 10:00 AM - 3:00 PM**

### Attendees
- K. Mani Vignesh (Product Owner)
- M. Manish Kumar Reddy (Scrum Master)
- D. Naga Gowtham Raj (Developer)
- Stakeholders

### Demonstration
✅ User registration with email verification  
✅ Login and session management  
✅ Profile creation and editing  
✅ Password reset functionality  

### Stakeholder Feedback
- **Positive:** Clean UI design, smooth registration flow
- **Suggestions:** Add social login options in future sprints
- **Concerns:** None

### Key Decisions
1. ✅ All sprint deliverables completed successfully
2. ✅ Authentication foundation ready for Sprint 2
3. ✅ Proceed with donation workflow in next sprint
4. ✅ No major blockers identified

---

## Sprint Retrospective

### Date & Time
**March 31, 2026 | 3:00 PM - 5:00 PM**

### Attendees
- K. Mani Vignesh (Product Owner)
- M. Manish Kumar Reddy (Scrum Master)
- D. Naga Gowtham Raj (Developer)

### What Went Well ✅
1. **Clear Sprint Goal:** Authentication focus kept team aligned
2. **Good Task Breakdown:** 22 tasks were well-sized and manageable
3. **Email Integration:** SMTP setup completed smoothly
4. **UI Consistency:** Tailwind CSS provided consistent styling
5. **Zero Blockers:** No major impediments during sprint

### What Could Be Improved 🔄
1. **Sprint Planning:** Need more detailed task estimation
2. **Daily Standups:** Should be more time-boxed (15 minutes max)
3. **Code Reviews:** Implement peer review process
4. **Documentation:** Add inline code comments
5. **Testing:** Increase automated test coverage

### Action Items for Sprint 2
| **Action Item** | **Owner** | **Priority** |
|-----------------|-----------|--------------|
| Improve sprint planning with detailed estimation | Mani Vignesh | High |
| Implement peer code review process | Manish Kumar | High |
| Increase team coordination meetings | Gowtham Raj | Medium |
| Add more inline documentation | All Team | Medium |
| Set up automated testing framework | Manish Kumar | Low |

### Team Morale
**Rating:** 9/10 - Excellent team collaboration and successful sprint completion

---

## Deployment Status

### Staging Environment
- **Deployed:** March 31, 2026 at 5:00 PM
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
- **Issue #1:** Email delivery delay during testing
  - **Resolution:** Configured SMTP timeout settings
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
- **Branch:** sprint-1-authentication
- **Commits:** 47 commits
- **Lines of Code:** ~2,500 lines

---

## Next Sprint Preview

### Sprint 2 Goals
- Implement donation creation workflow
- Add map integration with Leaflet.js
- Create donation request system
- Implement pickup scheduling

### Estimated Story Points
- 23 points (STORY-5, STORY-6, STORY-7, STORY-8)

---

## Sign-off

| **Role** | **Name** | **Signature** | **Date** |
|----------|----------|---------------|----------|
| **Product Owner** | K. Mani Vignesh | _______________ | March 31, 2026 |
| **Scrum Master** | M. Manish Kumar Reddy | _______________ | March 31, 2026 |
| **Developer** | D. Naga Gowtham Raj | _______________ | March 31, 2026 |

---

**Report Generated:** March 31, 2026  
**Sprint Status:** ✅ COMPLETED SUCCESSFULLY  
**Next Sprint Start:** April 1, 2026
