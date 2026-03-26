# **Product Requirements Document (PRD)**

**Product:** AI Presentation Feedback Web App  
 **Version:** 1.0  
 **Delivery Window:** 8 weeks  
 **Platform:** Django Monolith on PythonAnywhere

---

## **1\. Purpose**

This document defines the **functional, technical, and non-functional requirements** for building a lean web application that allows users to upload PDF presentations and receive AI-generated feedback asynchronously.

The goal is to deliver a **production-grade MVP** that integrates an existing LLM API and provides a clean, minimal user experience.

---

## **2\. Objectives**

### **Primary Objectives**

* Enable users to upload large PDF decks (up to **200MB**).

* Process presentations asynchronously using an existing LLM API.

* Provide centralized access to all uploaded PDFs and their feedback.

* Ensure **non-blocking UX** during processing.

* Deliver within **8 weeks** using a small, experienced team.

### **Non-Objectives**

* Slide editing or annotation tools

* Real-time collaboration

* Role-based access control beyond admin/non-admin

* Multi-tenant org separation

---

## **3\. Assumptions**

* LLM API is stable, versioned, and reachable over HTTPS.

* PythonAnywhere is the hosting environment (resource-constrained).

* Team prefers **Django-first** with minimal JS.

* All authenticated users can view all PDFs.

* Only admins can delete PDFs.

---

## **4\. Users & Permissions**

| Role | Capabilities |
| ----- | ----- |
| Authenticated User | Upload PDFs, view all PDFs, view all feedback |
| Admin | All above \+ delete PDFs, view system logs (stretch) |

---

## **5\. In-Scope Features**

1. Authentication

2. PDF upload (≤ 200MB)

3. Asynchronous processing

4. LLM API integration

5. Central PDF library

6. Feedback viewer

7. In-app notifications

8. Admin deletion controls

---

## **6\. Functional Requirements**

---

### **FR-01 Authentication**

**Description**  
 Users must authenticate to access the system.

**Acceptance Criteria**

* Users cannot access any page without login.

* Session-based auth via Django.

* Password reset optional if time allows.

---

### **FR-02 PDF Upload**

**Description**  
 Users can upload PDF versions of presentations.

**Rules**

* Max file size: **200MB**

* Allowed file type: `.pdf` only

* Virus scanning: optional (future hardening)

**Acceptance Criteria**

* System rejects non-PDF uploads.

* Upload progress indicator shown.

* On success:

  * Presentation record created.

  * Status set to `PENDING`.

---

### **FR-03 Asynchronous Processing**

**Description**  
 PDFs are processed in the background; users do not wait.

**Flow**

1. Upload completes

2. Presentation status → `PROCESSING`

3. Background worker sends PDF to LLM API

4. API response saved

5. Status → `COMPLETE` or `FAILED`

**Acceptance Criteria**

* User can navigate away immediately after upload.

* Processing continues reliably.

* Failures recorded with error message.

---

### **FR-04 LLM API Integration**

**Endpoint Contract (given)**

`{`  
  `"summary": "str",`  
  `"detailed_feedback": "str",`  
  `"input_tokens": 123,`  
  `"output_tokens": 456,`  
  `"time_stamp": "2026-01-12T10:15:00Z"`  
`}`

**System Responsibilities**

* POST PDF to API endpoint.

* Capture response.

* Persist:

  * Summary

  * Detailed feedback

  * Token usage

  * Timestamp

**Acceptance Criteria**

* API errors are retried twice.

* Hard failure sets status \= `FAILED`.

* Timeout \< 60s.

---

### **FR-05 Central PDF Library**

**Description**  
 All users can access a central repository of uploaded PDFs.

**Table Columns**

* File name

* Uploaded by

* Upload timestamp

* Processing status

* File size

* Page count

* Summary feedback

* API timestamp

**Acceptance Criteria**

* Table loads in \< 2s for 500 records.

* Status is visually clear (badge/label).

* Clicking a row opens feedback view.

---

### **FR-06 Feedback Viewer**

**Description**  
 Users can view full feedback for each presentation.

**View Sections**

1. Metadata panel

2. Summary feedback

3. Detailed feedback (scrollable)

**Acceptance Criteria**

* Feedback visible only when status \= `COMPLETE`.

* Clear error state when `FAILED`.

---

### **FR-07 In-App Notifications**

**Description**  
 Users receive in-app notification when processing completes.

**Mechanism**

* Polling or lightweight AJAX every 20–30s.

* Toast/modal appears when:

  * A previously `PROCESSING` item → `COMPLETE`.

**Acceptance Criteria**

* No page refresh required.

* Notification fires once per document.

---

### **FR-08 Admin Controls**

**Description**  
 Admins can delete PDFs manually.

**Acceptance Criteria**

* Delete removes:

  * File

  * DB records

* Action is irreversible.

* Audit log entry created (stretch).

---

## **7\. Non-Functional Requirements**

| Category | Requirement |
| ----- | ----- |
| Performance | Upload up to 200MB without timeout |
| Reliability | Background jobs must survive worker restarts |
| Security | Auth required for all endpoints |
| Scalability | Support 50 concurrent users |
| Maintainability | Clear service boundaries |
| Auditability | Track uploads, processing time, failures |
| UX | Clean, minimal, modern |

---

## **8\. Technical Architecture**

---

### **8.1 High-Level System**

`Browser`  
   `|`  
`Django Web App`  
   `|`  
`PostgreSQL`  
   `|`  
`Async Worker (Django-Q ORM)`  
   `|`  
`External LLM API`

---

### **8.2 Component Responsibilities**

#### **Django Monolith**

* Auth

* Upload handling

* UI rendering

* Job orchestration

* Notifications

#### **Async Worker**

* API calls

* Retry logic

* Result persistence

---

## **9\. Technology Stack**

### **Core**

* **Django 4.x**

* PostgreSQL

* Django-Q (ORM backend)

* Gunicorn

* Nginx (PythonAnywhere default)

### **Supporting**

* Requests (API calls)

* django-widget-tweaks (forms)

* django-crispy-forms (UI polish)

---

## **10\. Data Model (Final)**

### **User**

* id

* email

* password

### **Presentation**

* id

* file\_name

* file\_path

* file\_size

* page\_count

* uploaded\_by

* uploaded\_at

* status (`PENDING`, `PROCESSING`, `COMPLETE`, `FAILED`)

### **Feedback**

* id

* presentation\_id

* summary

* detailed\_feedback

* input\_tokens

* output\_tokens

* api\_timestamp

* created\_at

---

## **11\. Background Job Design**

### **Task: `process_presentation(presentation_id)`**

**Steps**

1. Fetch PDF from storage

2. POST to LLM API

3. Parse response

4. Save feedback

5. Update status

6. Emit completion event

**Retry Policy**

* 2 retries

* Exponential backoff

* On failure → status \= `FAILED`

---

## **12\. UX Principles**

* White space \> decoration

* Typography \> color

* No dashboards, just clarity

* Status always visible

* Fewer clicks \> more views

---

## **14\. Risks & Controls**

| Risk | Control |
| ----- | ----- |
| 200MB uploads overload | Enforce size limits \+ chunk upload |
| PythonAnywhere worker limits | Use Django-Q ORM backend |
| LLM API instability | Retry \+ circuit breaker |
| Slow UI updates | Polling-based notifications |
| Tight timeline | Strict MVP scope |

---

## **15\. Open Items (Optional Enhancements)**

* Email notifications

* File preview thumbnails

* Token usage dashboard

* Admin audit logs

* PDF text extraction fallback

---

## **16\. Definition of Done (MVP)**

The product is **done** when:

* Users can upload 200MB PDFs.

* Processing is asynchronous.

* LLM API is integrated and stable.

* All users can view all PDFs.

* Feedback is visible per presentation.

* In-app notifications work.

* Admin can delete PDFs.

* App is deployed on PythonAnywhere.

* Basic documentation exists.

---

If you’d like, next I can produce:

* 📦 **Jira-ready Epics & User Stories**

* 🏗️ **Detailed Technical Architecture Spec**

* 🧪 **Test Strategy & UAT Plan**

* 📐 **Wireframe-level UI spec**

