# Tuition-Go Backend Services Documentation

**Last Updated**: April 1, 2026  
**API Version**: 1.0

---

## Quick Start
- **Gateway URL**: `http://localhost:8000`
- **All requests** go through Kong Gateway → routed to appropriate service
- **Auth**: JWT Bearer token (handled by Kong middleware)

## Table of Contents
1. [API Gateway & Authentication](#api-gateway--authentication)
2. [Service Overview](#service-overview)
3. [Atomic Services](#atomic-services)
4. [Composite Services](#composite-services)
5. [Common Workflows](#common-workflows)

---

## API Gateway & Authentication

### Kong Gateway
Single entry point routing all requests to microservices.
- **URL**: `http://localhost:8000`
- **Config**: `backend/kong-gateway/kong.yml`

### JWT Authentication (Kong Middleware)

Kong validates all authenticated requests using JWT:

```
Client Request → Kong Gateway
                 ↓
          Validate JWT Token
          (signature, expiry, claims)
                 ↓
        ✓ Valid → Route to service
        ✗ Invalid → 401 Unauthorized
```

**Token Format**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Token Validation**:
- Kong verifies JWT signature using `JWT_SECRET_KEY`
- Checks token expiry
- Forwards auth header to downstream services
- Services can access token claims for user context

**Example Request**:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/session/session-123
```

### Route Mapping

| Path | Service | Port | Auth |
|------|---------|------|------|
| `/student/*` | Student | 5001 | Per-endpoint |
| `/tutor/*` | Tutor | 5002 | Per-endpoint |
| `/session/*` | Session | 5003 | Per-endpoint |
| `/meeting/*` | Meeting | 5004 | No |
| `/calendar/*` | Calendar | 5005 | Yes |
| `/email/*` | Email | 5006 | No |
| `/payment/*` | Payment | 5007 | Per-endpoint |
| `/checkout/*` | Checkout | 5100 | Yes |
| `/rate-tutor/*` | Rate Tutor | 5102 | No |
| `/getsessions/*` | Get Sessions | 5103 | No |
| `/process-booking/*` | Process Booking | 5104 | **Yes (Required)** |
| `/cancel-session/*` | Cancel Session | 5101 | No |

---

## Service Overview

---

## Atomic Services

Core services that handle specific business domains. Each has its own database.

### 1. Student Service (Port 5001)
Manages student profiles and accounts.

**Key Endpoints**:
- `POST /student/register` - Create student account
- `GET /student/<id>` - Get profile
- `PUT /student/<id>` - Update profile (with file upload)
- `GET /student/by-clerk/<clerkId>` - Get by Clerk user ID
- `DELETE /student/<id>` - Delete account

**Auth**: Public for register, required for others

---

### 2. Tutor Service (Port 5002)
Manages tutor profiles, subjects, and ratings.

**Key Endpoints**:
- `POST /tutor/register` - Create tutor (Gmail required)
- `GET /tutor/all` - List all tutors
- `GET /tutor/search` - Search by subject, level, name, rating
- `GET /tutor/<id>` - Get profile with subjects
- `PUT /tutor/<id>` - Update profile & bio
- `PUT /tutor/<id>/updateRating` - Update tutor rating
- `POST /tutor/<id>/subjects` - Add subject offering
- `GET /tutor/<id>/subjects` - List tutor's subjects
- `PUT/DELETE /tutor/<id>/subjects/<subjectId>` - Manage subjects

**Auth**: Public for GET, required for modifying data

---

### 3. Session Service (Port 5003)
Manages tutoring session records (calendar, scheduling).

**Key Endpoints**:
- `POST /session/session` - Create session (checks overlaps)
- `GET /session/<id>` - Get session details
- `GET /session/all` - Get sessions (filter by tutorId/studentId)
- `PUT /session/<id>` - Update session
- `DELETE /session/<id>` - Cancel session

**Auth**: Required for create/update/delete

---

### 4. Payment Service (Port 5007)
Handles Stripe payment processing.

**Key Endpoints**:
- `GET /payment/config` - Get Stripe publishable key (public)
- `POST /payment/create-checkout-session` - Create Stripe checkout
- `POST /payment/verify` - Verify payment completion

**Auth**: Required for checkout & verify

**External**: Stripe API

---

### 5. Calendar Service (Port 5005)
Creates Google Calendar events with Meet links.

**Key Endpoints**:
- `POST /calendar/create-meeting` - Create calendar event + Meet link
- `POST /calendar/update-meeting` - Add attendee to event

**Auth**: Required

**External**: Google Calendar API

---

### 6. Email Service (Port 5006)
Notification system (scaffolded - not yet implemented).

**Status**: ⚠️ Placeholder only

---

### 7. Meeting Service (Port 5004)
Meeting management (scaffolded - not yet implemented).

**Status**: ⚠️ Placeholder only

---

## Composite Services

Orchestrate atomic services for complex workflows.

### 1. Checkout Service (Port 5100)
Initiates payment for a session.

**Endpoint**:
- `POST /checkout/checkout` - Orchestrate checkout

**Input**:
```json
{
  "session_id": "session-uuid-789",
  "student_id": "student-uuid-456"
}
```

**Exact Orchestration** (in sequence):

1. **Fetch Session Details**
   ```
   GET http://session:5003/session/session-uuid-789
   Headers: Authorization (forwarded)
   Response: { sessionId, tutorId, tutorSubjectId, startTime, endTime, durationMins, ... }
   ```

2. **Fetch Tutor Details**
   ```
   GET http://tutor:5002/tutor/{tutorId from session}
   Response: { tutorId, name, averageRating, totalReviews, ... }
   ```

3. **Fetch Tutor Subjects (for pricing)**
   ```
   GET http://tutor:5002/tutor/{tutorId}/subjects
   Response: [{ subjectId, tutorId, subject, academicLevel, hourlyRate }, ...]
   ```

4. **Find matching subject & calculate price**
   ```
   Match: tutorSubjectId from session with subjects array
   Calculate: hourlyRate × (durationMins / 60) = totalPrice
   ```

5. **Create Stripe Checkout Session**
   ```
   POST http://payment:5007/payment/create-checkout-session
   Headers: Authorization (forwarded)
   Body: {
     title: "{subject} Tutoring Session",
     description: "1 hour {subject} {academicLevel} with {tutorName}",
     amount: totalPrice (in cents),
     tutor_name: tutorName,
     subject: subjectName,
     lesson_date: startTime,
     session_id: sessionId,
     student_id: studentId,
     tutor_id: tutorId
   }
   Response: { checkout_url, session_id }
   ```

**Output**:
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_live_...",
  "session_id": "cs_live_...",
  "session_details": { ... },
  "tutor_details": { name, hourlyRate, ... }
}
```

**Auth**: Required

**Calls**: Session (5003) → Tutor (5002) → Payment (5007)

---

### 2. Get Sessions Service (Port 5103)
Retrieves sessions with enriched data (tutor/student details, pricing).

**Endpoints**:
- `GET /getsessions/student/<studentId>/sessions` - Student's sessions
- `GET /getsessions/tutor/<tutorId>/sessions` - Tutor's sessions
- `GET /getsessions/session/<sessionId>` - Single session

**Orchestration A: Get Student Sessions**

**Input**: `studentId` (path parameter)

**Exact Flow**:

1. **Fetch all sessions for student**
   ```
   GET http://session:5003/session/all?studentId=student-uuid-456
   Response: [
     { sessionId, tutorId, tutorSubjectId, studentId, startTime, endTime, durationMins, ... },
     ...
   ]
   ```

2. **For each session, enrich with tutor data**:
   ```
   GET http://tutor:5002/tutor/{tutorId}
   Response: { tutorId, name, imageURL, ... }
   ```

3. **For each session, get tutor subject/price**:
   ```
   GET http://tutor:5002/tutor/{tutorId}/subjects
   Find: matching tutorSubjectId
   Extract: subject, academicLevel, hourlyRate
   Calculate: totalPrice = hourlyRate × (durationMins / 60)
   ```

**Output** (array):
```json
[
  {
    "sessionId": "...",
    "tutorId": "...",
    "studentId": "...",
    "tutorName": "Dr. Alice Smith",
    "tutorImageUrl": "https://...",
    "subjectName": "Mathematics",
    "academicLevel": "GCSE",
    "totalPrice": 35.00,
    "startTime": "2025-04-15T14:00:00Z",
    ...
  }
]
```

---

**Orchestration B: Get Tutor Sessions**

**Input**: `tutorId` (path parameter)

**Exact Flow**:

1. **Fetch all sessions for tutor**
   ```
   GET http://session:5003/session/all?tutorId=tutor-uuid-123
   Response: [
     { sessionId, tutorId, studentId, tutorSubjectId, ... },
     ...
   ]
   ```

2. **Enrich with tutor data** (same as student endpoint):
   ```
   GET http://tutor:5002/tutor/{tutorId}
   GET http://tutor:5002/tutor/{tutorId}/subjects
   → Extract: name, imageURL, subject, hourlyRate
   → Calculate: totalPrice
   ```

3. **Additionally, enrich with student data** ⚠️ (this is the difference):
   ```
   GET http://student:5001/student/{studentId}
   Response: { studentId, name, imageURL, email, phone, ... }
   ```

**Output** (array):
```json
[
  {
    "sessionId": "...",
    "tutorId": "...",
    "studentId": "...",
    "tutorName": "Dr. Alice Smith",
    "tutorImageUrl": "https://...",
    "studentName": "John Doe",
    "studentImageUrl": "https://...",
    "subjectName": "Mathematics",
    "academicLevel": "GCSE",
    "totalPrice": 35.00,
    ...
  }
]
```

---

**Orchestration C: Get Single Session**

**Input**: `sessionId` (path parameter)

**Exact Flow**:

1. **Fetch specific session**
   ```
   GET http://session:5003/session/session-uuid-789
   Response: { sessionId, tutorId, studentId, tutorSubjectId, ... }
   ```

2. **Enrich with tutor & subject data** (same as tutor endpoint):
   ```
   GET http://tutor:5002/tutor/{tutorId}
   GET http://tutor:5002/tutor/{tutorId}/subjects
   ```

3. **Enrich with student data** (same as tutor endpoint):
   ```
   GET http://student:5001/student/{studentId}
   ```

**Output** (single object):
```json
{
  "sessionId": "...",
  "tutorId": "...",
  "studentId": "...",
  "tutorName": "...",
  "tutorImageUrl": "...",
  "studentName": "...",
  "studentImageUrl": "...",
  "subjectName": "...",
  "totalPrice": 35.00
}
```

**Auth**: Not required

**Calls**: Session (5003) → Tutor (5002) → Student (5001)

---

### 3. Process Booking Service (Port 5104)
Completes booking after successful payment.

**Endpoint**:
- `POST /process-booking/process-booking` - Process booking

**Input**:
```json
{
  "stripe_session_id": "cs_live_abc123xyz"
}
```

**Headers Required**: `Authorization: Bearer <JWT_TOKEN>`

**Exact Orchestration** (in sequence):

1. **Validate JWT Token** ⚠️ **CRITICAL**
   ```
   Kong Gateway validates token signature & expiry
   If invalid → 401 Unauthorized
   If valid → Continue with claims available
   ```

2. **Verify Stripe Payment**
   ```
   POST http://payment:5007/payment/verify
   Headers: Authorization (forwarded)
   Body: { stripe_session_id: "cs_live_abc123xyz" }
   Response: {
     payment_status: "paid",
     session_id: "session-uuid-789",
     student_id: "student-uuid-456",
     tutor_id: "tutor-uuid-123",
     amount_total: 3500
   }
   ```

3. **Update Session Status to "booked"**
   ```
   PUT http://session:5003/session/{sessionId from payment}
   Headers: Authorization (forwarded)
   Body: { status: "booked" }
   Response: { sessionId, status, updatedAt, ... }
   ```

4. **Fetch Student Details**
   ```
   GET http://student:5001/student/{studentId from payment}
   Response: {
     studentId, name, email, phone, imageURL, ...
   }
   ```

5. **Fetch Tutor Details**
   ```
   GET http://tutor:5002/tutor/{tutorId from payment}
   Response: {
     tutorId, name, clerkUserId, email, imageURL, ...
   }
   ```

6. **Add Student to Google Calendar**
   ```
   POST http://calendar:5005/calendar/update-meeting
   Headers: Authorization (forwarded)
   Body: {
     eventId: session.calendarEventId,
     tutorClerkId: tutor.clerkUserId,
     studentEmail: student.email
   }
   Response: { message, eventId }
   ```

**Final Output**:
```json
{
  "message": "Booking completed successfully",
  "sessionId": "session-uuid-789",
  "studentId": "student-uuid-456",
  "tutorId": "tutor-uuid-123",
  "status": "booked",
  "amount_paid": 3500,
  "meeting_link": "https://meet.google.com/abc-def-ghi",
  "student_name": "John Doe",
  "tutor_name": "Dr. Alice Smith"
}
```

**Error Cases**:
- `401 Unauthorized` - Invalid/expired JWT token
- `400 Bad Request` - Payment verification failed (not paid)
- `404 Not Found` - Session/student/tutor not found
- `500 Internal Server Error` - Calendar API failed

**Auth**: **Required (JWT token is critical)**

**Calls** (in order): Token Validation → Payment (5007) → Session (5003) → Student (5001) → Tutor (5002) → Calendar (5005)

---

### 4. Cancel Session Service (Port 5101)
Session cancellation (scaffolded - not yet implemented).

**Status**: ⚠️ Placeholder only

---

### 5. Rate Tutor Service (Port 5102)
Tutor rating system (scaffolded - not yet implemented).

**Status**: ⚠️ Placeholder only

---

## Common Workflows

### Workflow 1: Student Books a Session
```
1. Search tutors → GET /tutor/search
2. View tutor → GET /tutor/<id>
3. Create session → POST /session/session
4. Checkout → POST /checkout/checkout (returns Stripe URL)
5. Pay via Stripe
6. Process booking → POST /process-booking/process-booking (JWT required)
   → Confirms payment, updates session, adds to calendar
7. Meeting ready with Meet link
```

### Workflow 2: Tutor View Sessions
```
1. Get sessions → GET /getsessions/tutor/<tutorId>/sessions
   → Returns all sessions with student details & pricing
2. View single session → GET /getsessions/session/<sessionId>
   → Full enrichment: tutor + student + subjects
```

### Workflow 3: Rate After Session
```
1. Student rates tutor → PUT /tutor/<tutorId>/updateRating
   → Updates averageRating & totalReviews
2. Tutor profile now shows new rating
3. Affects tutor search ranking
```

---

## Database & Storage

**PostgreSQL**: Student, Tutor, Session, Tutor Subjects data  
**Google Calendar**: Calendar events + Meet links  
**Stripe**: Payments (external API)  

---

## Key Points

✅ **12 Services**: 7 atomic + 5 composite  
✅ **Kong Gateway**: Single entry point with JWT auth  
✅ **Service Discovery**: Environment variables for inter-service URLs  
✅ **Timeout**: 5 seconds for all service-to-service calls  
✅ **CORS**: Enabled on all services  

⚠️ **Not Yet Implemented**:
- Email Service (scaffolded)
- Meeting Service (scaffolded)
- Cancel Session Service (scaffolded)
- Rate Tutor Service (scaffolded)

---

## Deployment

```bash
cd backend
docker-compose up -d
```

All services start automatically. Access via: `http://localhost:8000`

---

## Status Summary

| Service | Type | Status | Critical |
|---------|------|--------|----------|
| Student | Atomic | ✅ Active | Yes |
| Tutor | Atomic | ✅ Active | Yes |
| Session | Atomic | ✅ Active | Yes |
| Payment | Atomic | ✅ Active | Yes |
| Calendar | Atomic | ✅ Active | Yes |
| Meeting | Atomic | ⚠️ Scaffolded | No |
| Email | Atomic | ⚠️ Scaffolded | No |
| Checkout | Composite | ✅ Active | Yes |
| Get Sessions | Composite | ✅ Active | Yes |
| Process Booking | Composite | ✅ Active | Yes** |
| Cancel Session | Composite | ⚠️ Scaffolded | No |
| Rate Tutor | Composite | ⚠️ Scaffolded | No |

** Requires JWT token for Kong auth
