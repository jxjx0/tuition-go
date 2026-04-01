# TuitionGo — Services Documentation

**Last Updated**: April 2, 2026
**Stack**: Flask microservices · Kong API Gateway · Clerk (JWT) · Supabase (PostgreSQL) · Google Calendar · Stripe · OutSystems (external reviews)

---

## How It Works (Big Picture)

```
Browser (Vue 3)
      │
      │  All requests to http://localhost:8000
      ▼
Kong API Gateway  ──── validates JWT (Clerk RS256) on protected routes
      │
      ├─── Atomic Services (own their data)
      │       Student (5001) · Tutor (5002) · Session (5003)
      │       Payment (5007) · Calendar (5005)
      │
      └─── Composite Services (orchestrate atomics)
              Checkout (5100) · Process Booking (5104)
              Create/Update/Delete Session (5105/5106/5107)
              Cancel Session (5101) · Get Sessions (5103)
              Rate Tutor (5102) · Get Tutor (5109)
```

**Rule**: Composite services call atomic services. Atomic services never call each other.

---

## Gateway Route Map

All frontend requests use the prefix `/api/v1/...`

| Frontend Path Prefix | Routes To | Port | Auth |
|---|---|---|---|
| `/api/v1/students` | Student | 5001 | ✅ JWT |
| `/api/v1/tutors` | Tutor | 5002 | ✅ JWT |
| `/api/v1/sessions` | Session | 5003 | ✅ JWT |
| `/api/v1/meetings` | Meeting | 5004 | ✅ JWT |
| `/api/v1/calendar` | Calendar | 5005 | GET public, others ✅ JWT |
| `/api/v1/emails` | Email | 5006 | No auth |
| `/api/v1/payments` | Payment | 5007 | ✅ JWT |
| `/api/v1/checkout` | Checkout | 5100 | ✅ JWT |
| `/api/v1/process-booking` | Process Booking | 5104 | ✅ JWT |
| `/api/v1/create-session` | Create Session | 5105 | ✅ JWT |
| `/api/v1/update-session` | Update Session | 5106 | ✅ JWT |
| `/api/v1/delete-session` | Delete Session | 5107 | ✅ JWT |
| `/api/v1/cancel-session` | Cancel Session | 5101 | ✅ JWT |
| `/api/v1/rate-tutor` | Rate Tutor | 5102 | ✅ JWT |
| `/api/v1/getsessions` | Get Sessions | 5103 | ✅ JWT |
| `/api/v1/get-tutor` | Get Tutor | 5109 | ✅ JWT |
| `/api/v1/reviews` | OutSystems (external) | — | ✅ JWT |

---

---

# SECTION 1 — BOOKING FLOW

This covers everything from browsing tutors to completing a paid booking. Also includes tutor-side session management (create, edit, delete, complete).

---

## 1.1 Browse Tutors

**Page**: `BrowseTutorsPage2.vue`

```
Frontend  →  GET /api/v1/tutors/search?name=&subject=&level=&minRating=
          ←  [{ tutorId, name, imageURL, bio, averageRating, totalReviews, subjects[] }]
```

**Atomic**: Tutor Service (5002)
`GET /tutor/search` — filters by name, subject, academic level, min rating

---

## 1.2 View Tutor Detail

**Page**: `TutorDetailPage2.vue`

Two parallel calls on mount:

```
Frontend  →  GET /api/v1/get-tutor/<tutorId>          (composite)
          ←  { tutorId, name, imageURL, bio, averageRating, totalReviews,
                subjects[], reviews[{ ..., studentName, studentAvatar }] }

Frontend  →  GET /api/v1/sessions/all?tutorId=<id>    (atomic, for available slots)
          ←  [{ sessionId, startTime, endTime, status, tutorSubjectId, ... }]
```

The get-tutor composite (5109) internally calls:
1. `GET /tutor/<id>` → tutor profile
2. `GET /review/<tutorId>` → OutSystems reviews
3. `GET /student/<studentId>` for each reviewer → adds `studentName`, `studentAvatar`

---

## 1.3 Book a Session (Student)

**Page**: `SessionDetailPage.vue` → `PaymentSuccess.vue`

### Step 1 — Load session details

```
Frontend  →  GET /api/v1/getsessions/session/<sessionId>    (composite)
          ←  { sessionId, tutorId, tutorName, tutorImageUrl,
                subjectName, academicLevel, totalPrice,
                startTime, endTime, status, meetingLink, ... }
```

Get Sessions composite (5103) calls:
- `GET /session/<id>` → session record
- `GET /tutor/<tutorId>` → tutor name, image
- `GET /tutor/<tutorId>/subjects` → subject name, hourly rate → calculates `totalPrice`
- `GET /student/<studentId>` → student name, image (if booked)

### Step 2 — Initiate checkout

```
Frontend  →  POST /api/v1/checkout/checkout
             Body: { session_id, student_id }
          ←  { checkout_url: "https://checkout.stripe.com/..." }

Frontend  →  window.location.href = checkout_url    (redirect to Stripe)
```

Checkout composite (5100) calls:
1. `GET /session/<id>` → session record
2. `GET /tutor/<tutorId>` → tutor name
3. `GET /tutor/<tutorId>/subjects` → hourly rate → calculates price in cents
4. `POST /payment/create-checkout-session` → creates Stripe session, returns URL

### Step 3 — Process booking after payment

Stripe redirects back to `/payment-success?session_id=<stripe_id>`

```
Frontend  →  POST /api/v1/process-booking/process-booking
             Body: { stripe_session_id: "cs_live_..." }
          ←  { message, sessionId, status: "booked", meeting_link,
                student_name, tutor_name, amount_paid }
```

Process Booking composite (5104) calls:
1. `POST /payment/verify` → confirms payment is `paid`, extracts session/student/tutor IDs
2. `PUT /session/<id>` → sets `status = "booked"`, links `studentId`
3. `GET /student/<studentId>` → student email (for calendar invite)
4. `GET /tutor/<tutorId>` → tutor clerkUserId (for calendar)
5. `POST /calendar/update-meeting` → adds student as attendee to the Google Calendar event

**Session status after this step**: `booked`

---

## 1.4 Student Dashboard — View Sessions

**Page**: `StudentDashboardPage.vue`

```
Frontend  →  GET /api/v1/getsessions/student/<studentId>/sessions
          ←  [{ sessionId, tutorName, tutorImageUrl, subjectName,
                 academicLevel, totalPrice, startTime, endTime,
                 status, meetingLink, durationMins }]
```

Sessions are filtered client-side into tabs: Upcoming · Completed · Cancelled

---

## 1.5 Student Session Detail

**Page**: `SessionDetailPage.vue`

```
Frontend  →  GET /api/v1/getsessions/session/<sessionId>
          ←  { full enriched session with tutor + student info }
```

---

## 1.6 Tutor Dashboard — View Sessions

**Page**: `TutorDashboardPage.vue`

```
Frontend  →  GET /api/v1/getsessions/tutor/<tutorId>/sessions
          ←  [{ sessionId, studentName, studentImageUrl, subjectName,
                 totalPrice, startTime, endTime, status, meetingLink, ... }]
```

Sessions filtered client-side into 4 tabs: Booked · Available · Completed · Cancelled

---

## 1.7 Tutor Creates a Session Slot

**Page**: `TutorDashboardPage.vue` (Create Session Slot form)

```
Frontend  →  POST /api/v1/create-session/create-session
             Body: { tutorId, tutorSubjectId, startTime, endTime,
                     durationMins, summary, timezone }
          ←  { sessionId, status: "available", calendarEventId, meetingLink, ... }
```

Create Session composite (5105) calls:
1. `POST /session/session` → creates session record with `status = "available"`
2. `POST /calendar/create-meeting` → creates Google Calendar event, generates Meet link
3. `PUT /session/<id>` → patches session with `calendarEventId` + `meetingLink`

**On 409**: Tutor already has an overlapping session at that time

---

## 1.8 Tutor Edits a Session

**Page**: `TutorSessionEditPage.vue`

```
Frontend  →  PUT /api/v1/update-session/<sessionId>
             Body: { tutorSubjectId, startTime, endTime, durationMins,
                     summary, timezone }
          ←  { updated session object }
```

Update Session composite (5106) calls:
1. `GET /session/<id>` → checks session exists and is not `booked` (blocked if booked)
2. `PUT /session/<id>` → updates times, subject
3. `GET /tutor/<tutorId>` → gets `clerkUserId` for calendar API
4. `POST /calendar/reschedule-meeting` → updates Google Calendar event times

---

## 1.9 Tutor Deletes a Session

**Page**: `TutorSessionEditPage.vue`

```
Frontend  →  DELETE /api/v1/delete-session/<sessionId>
          ←  { message: "Session and calendar event deleted successfully" }
```

Delete Session composite (5107) calls:
1. `GET /session/<id>` → checks session exists and is not `booked` (blocked if booked)
2. `DELETE /session/<id>` → hard-deletes the session record
3. `GET /tutor/<tutorId>` → gets `clerkUserId` for calendar API
4. `POST /calendar/delete-meeting` → removes the Google Calendar event

---

## 1.10 Tutor Marks Session as Complete

**Page**: `TutorSessionEditPage.vue` — "Mark as Complete" button (only shows after `endTime`)

```
Frontend  →  POST /api/v1/sessions/<sessionId>/complete
             Body: { tutorId }
          ←  { sessionId, status: "completed", ... }
```

**Atomic only** — Session Service (5003) directly:
- Verifies `tutorId` matches the session's tutor
- Verifies `status === "booked"`
- Verifies `now > endTime` (session has actually ended)
- Updates `status = "completed"`

**Session status after this step**: `completed`

---

## Session Status Lifecycle

```
[available]  ──── student pays ────►  [booked]
                                           │
                                     session ends + tutor clicks complete
                                           │
                                           ▼
                                      [completed]  ──── student can now review ───►  Review Flow

[available/booked]  ─── cancel ───►  [cancelled]
```

---

---

# SECTION 2 — REVIEW FLOW

This covers what happens after a session is completed. A student can leave a review, and reviews are publicly visible on the tutor detail page.

---

## 2.1 Student Leaves a Review

**Page**: `ReviewPage.vue`
Navigated to from the student dashboard when session status is `completed`

### Step 1 — Load session + duplicate check

On mount, two calls run:

```
Frontend  →  GET /api/v1/getsessions/session/<sessionId>
          ←  { status, tutorId, tutorName, tutorImageUrl,
                subjectName, academicLevel, startTime, endTime }

             (if status !== "completed" → show error, no form)

Frontend  →  GET /api/v1/get-tutor/<tutorId>
          ←  { reviews: [{ session_id, student_id, rating, comment, ... }] }

             (if any review.session_id === sessionId → show "Already Reviewed" screen)
```

### Step 2 — Submit review

```
Frontend  →  POST /api/v1/rate-tutor/review
             Body: { session_id, tutor_id, rating (1-5), comment }
          ←  { message, review, tutorRating }
```

Rate Tutor composite (5102) calls:
1. `GET /session/<sessionId>` → verifies `status === "completed"`, confirms `tutorId` matches
2. `GET /review/<tutorId>` on OutSystems → checks no existing review for this `session_id` (409 if duplicate)
3. `POST /review` on OutSystems → saves the review (with `student_id`, `session_id`, `tutor_id`, `rating`, `comment`, `createdAt`)
4. `PUT /tutor/updateRating` → recalculates and stores the tutor's new `averageRating` and `totalReviews`

**On 409**: "You have already reviewed this session" (enforced both frontend and backend)

---

## 2.2 Tutor Detail Page — Show Reviews

**Page**: `TutorDetailPage2.vue`

Reviews are loaded as part of the single `GET /api/v1/get-tutor/<tutorId>` call (same as 1.2 above):

```
Frontend  →  GET /api/v1/get-tutor/<tutorId>
          ←  {
               tutorId, name, imageURL, bio, averageRating, totalReviews,
               subjects: [...],
               reviews: [
                 {
                   review_id, session_id, tutor_id, student_id,
                   rating, comment, createdAt,
                   studentName,    ← enriched by get-tutor composite
                   studentAvatar   ← enriched by get-tutor composite
                 }
               ]
             }
```

Get Tutor composite (5109) calls:
1. `GET /tutor/<id>` → tutor profile
2. `GET /review/<tutorId>` on OutSystems → raw reviews list
3. For each review: `GET /student/<student_id>` → adds `studentName`, `studentAvatar`

---

## 2.3 Tutor Dashboard — Recent Reviews Sidebar

**Page**: `TutorDashboardPage.vue`

Uses the same `GET /api/v1/get-tutor/<tutorId>` call as above. Reviews come back already enriched with student names and avatars.

```
Frontend  →  GET /api/v1/get-tutor/<tutorId>
          ←  { ..., reviews: [{ rating, comment, createdAt, studentName, studentAvatar }] }
```

---

## Review Data (OutSystems Schema)

OutSystems stores and returns review records in this shape:

```json
{
  "review_id": 1712345678000,
  "session_id": "9aeb38e9-...",
  "tutor_id":   "0e5767bb-...",
  "student_id": "d1234abc-...",
  "rating": 5,
  "comment": "Excellent session!",
  "createdAt": "2026-04-02T10:30:00.000000Z"
}
```

**External endpoints used**:
- `GET  /review/<tutorId>` → `{ data: { reviews: [...] } }`
- `POST /review` → create review

---

---

# Atomic Services Reference

These are the base services that own and persist data.

---

### Student Service — Port 5001

Manages student profiles stored in Supabase.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/student/register` | Create student profile |
| `GET`  | `/student/<id>` | Get student by UUID |
| `PUT`  | `/student/<id>` | Update profile (supports image upload) |
| `GET`  | `/student/by-clerk/<clerkId>` | Look up by Clerk user ID |
| `DELETE` | `/student/<id>` | Delete account |

---

### Tutor Service — Port 5002

Manages tutor profiles and subject offerings.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/tutor/register` | Create tutor profile |
| `GET`  | `/tutor/all` | List all tutors |
| `GET`  | `/tutor/search` | Filter by name, subject, level, rating |
| `GET`  | `/tutor/<id>` | Get tutor profile with subjects |
| `PUT`  | `/tutor/<id>` | Update bio, image |
| `POST` | `/tutor/<id>/subjects` | Add a subject offering |
| `GET`  | `/tutor/<id>/subjects` | List tutor's subjects |
| `PUT`  | `/tutor/<id>/subjects/<subjectId>` | Update subject |
| `DELETE` | `/tutor/<id>/subjects/<subjectId>` | Remove subject |
| `PUT`  | `/tutor/updateRating` | Recalculate average rating (called by rate-tutor composite) |

---

### Session Service — Port 5003

Manages session records. Status transitions: `available → booked → completed / cancelled`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/session/session` | Create session (checks overlaps) |
| `GET`  | `/session/<id>` | Get single session |
| `GET`  | `/session/all` | List sessions (filter: `?tutorId=` or `?studentId=`) |
| `PUT`  | `/session/<id>` | Update any field(s) |
| `DELETE` | `/session/<id>` | Hard-delete session |
| `POST` | `/session/<id>/complete` | Mark session complete (backend-validated) |

**Complete endpoint rules**: caller must be the session's tutor, status must be `booked`, current time must be after `endTime`.

---

### Payment Service — Port 5007

Wraps the Stripe API.

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/payment/config` | Get Stripe publishable key |
| `POST` | `/payment/create-checkout-session` | Create Stripe checkout URL |
| `POST` | `/payment/verify` | Verify completed payment, extract metadata |

---

### Calendar Service — Port 5005

Manages Google Calendar events with Meet links. Uses OAuth tokens per Clerk user.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/calendar/create-meeting` | Create event + Meet link |
| `POST` | `/calendar/update-meeting` | Add attendee to event |
| `POST` | `/calendar/reschedule-meeting` | Update event times |
| `POST` | `/calendar/delete-meeting` | Delete calendar event |

---

### Email Service — Port 5006 _(not yet implemented)_

Placeholder — no active endpoints.

---

---

# Composite Services Reference

---

### Checkout — Port 5100

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/checkout/checkout` | Validate session + calculate price + create Stripe checkout URL |

**Input**:
```json
{
  "session_id": "uuid",
  "student_id": "uuid"
}
```

**Output** `200`:
```json
{
  "url": "https://checkout.stripe.com/pay/cs_live_...",
  "id":  "cs_live_..."
}
```

**Errors**: `400` missing fields · `404` session or subject not found · `500` downstream failure

Calls: Session → Tutor → Payment

---

### Process Booking — Port 5104

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/process-booking/process-booking` | Confirm payment + mark session booked + send calendar invite to student |

**Input**:
```json
{
  "stripe_session_id": "cs_live_..."
}
```

**Output** `200`:
```json
{
  "message": "Booking confirmed and calendar updated",
  "sessionId": "uuid",
  "student_email": "student@example.com",
  "student_name": "John Doe",
  "tutor_name": "Alice Smith",
  "amount_paid": 3500,
  "start_time": "2026-04-10T14:00:00",
  "end_time": "2026-04-10T15:00:00",
  "subject": "Mathematics",
  "status": "booked"
}
```

**Output** `207` (calendar update failed, booking still confirmed):
```json
{
  "message": "Booking confirmed but calendar update failed",
  "calendarError": "...",
  ...same fields as 200...
}
```

**Errors**: `400` missing field · `401` invalid JWT · `402` payment not completed · `500` downstream failure

Calls: Payment → Session → Tutor → Student → Calendar

---

### Create Session — Port 5105

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/create-session/create-session` | Create session record + Google Calendar event + link them |

**Input**:
```json
{
  "tutorId":        "uuid",
  "tutorSubjectId": "uuid",
  "startTime":      "2026-04-10T14:00:00",
  "endTime":        "2026-04-10T15:00:00",
  "durationMins":   60,
  "summary":        "Mathematics (A-Level)",
  "timezone":       "Asia/Singapore"
}
```

**Output** `201`:
```json
{
  "sessionId":       "uuid",
  "tutorId":         "uuid",
  "tutorSubjectId":  "uuid",
  "startTime":       "2026-04-10T14:00:00",
  "endTime":         "2026-04-10T15:00:00",
  "durationMins":    60,
  "status":          "available",
  "calendarEventId": "google_event_id",
  "meetingLink":     "https://meet.google.com/abc-def-ghi"
}
```

**Output** `207` (session created, calendar failed):
```json
{
  "message": "Session created but calendar event failed",
  "session": { ... },
  "calendarError": "..."
}
```

**Errors**: `400` missing fields · `401` invalid JWT · `409` overlapping session exists

Calls: Session → Calendar → Session (patch)

---

### Update Session — Port 5106

| Method | Path | Description |
|--------|------|-------------|
| `PUT` | `/update-session/<sessionId>` | Update session times/subject + sync calendar. Blocked if status is `booked` |

**Input**:
```json
{
  "tutorSubjectId": "uuid",
  "startTime":      "2026-04-10T15:00:00",
  "endTime":        "2026-04-10T16:00:00",
  "durationMins":   60,
  "summary":        "Physics (A-Level)",
  "timezone":       "Asia/Singapore"
}
```

**Output** `200`: Updated session object (same shape as Create Session output)

**Output** `207` (session updated, calendar sync failed):
```json
{
  "message": "Session updated but calendar sync failed",
  "session": { ... },
  "calendarError": "..."
}
```

**Errors**: `400` missing fields · `401` invalid JWT · `404` session not found · `409` session is already booked

Calls: Session (read) → Session (update) → Tutor → Calendar

---

### Delete Session — Port 5107

| Method | Path | Description |
|--------|------|-------------|
| `DELETE` | `/delete-session/<sessionId>` | Delete session record + remove calendar event. Blocked if status is `booked` |

**Input**: None (sessionId in path)

**Output** `200`:
```json
{
  "message": "Session and calendar event deleted successfully"
}
```

**Output** `207` (session deleted, calendar cleanup failed):
```json
{
  "message": "Session deleted but calendar event cleanup failed",
  "calendarError": "..."
}
```

**Errors**: `401` invalid JWT · `404` session not found · `409` session is already booked

Calls: Session (read) → Session (delete) → Tutor → Calendar

---

### Cancel Session — Port 5101 _(not yet implemented)_

Placeholder — no active endpoints.

---

### Get Sessions — Port 5103

Retrieves sessions enriched with tutor/student details and calculated pricing.

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/getsessions/student/<studentId>/sessions` | All sessions for a student |
| `GET`  | `/getsessions/tutor/<tutorId>/sessions` | All sessions for a tutor (includes student info) |
| `GET`  | `/getsessions/session/<sessionId>` | Single session (fully enriched) |

**Input**: ID in path only, no body

**Output** `200` (array for student/tutor endpoints, single object for session endpoint):
```json
{
  "sessionId":      "uuid",
  "tutorId":        "uuid",
  "studentId":      "uuid",
  "tutorSubjectId": "uuid",
  "startTime":      "2026-04-10T14:00:00",
  "endTime":        "2026-04-10T15:00:00",
  "durationMins":   60,
  "status":         "booked",
  "meetingLink":    "https://meet.google.com/abc-def-ghi",
  "tutorName":      "Alice Smith",
  "tutorImageUrl":  "https://...",
  "subjectName":    "Mathematics",
  "academicLevel":  "A-Level",
  "totalPrice":     35.00,
  "studentName":    "John Doe",       // tutor + single endpoints only
  "studentImageUrl":"https://..."     // tutor + single endpoints only
}
```

**Errors**: `404` no sessions found · `500` downstream failure

Calls: Session → Tutor → Student (tutor/single endpoints only)

---

### Rate Tutor — Port 5102

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/rate-tutor/review` | Validate session, prevent duplicates, submit review, update tutor rating |

**Input**:
```json
{
  "session_id": "uuid",
  "tutor_id":   "uuid",
  "rating":     5,
  "comment":    "Excellent session!"
}
```

**Output** `200`:
```json
{
  "message": "Review submitted and tutor rating updated",
  "review": { "review_id": 1712345678000, ... },
  "tutorRating": { "averageRating": 4.8, "totalReviews": 12 }
}
```

**Output** `207` (review saved, rating update failed):
```json
{
  "message": "Review submitted but tutor rating update failed",
  "review": { ... },
  "ratingError": "..."
}
```

**Errors**: `400` missing/invalid fields · `404` session not found · `409` already reviewed this session · `500` OutSystems failure

Calls: Session → OutSystems (read check) → OutSystems (write) → Tutor (update rating)

---

### Get Tutor — Port 5109

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/get-tutor/<tutorId>` | Return tutor profile with enriched reviews (student name + avatar attached) |

**Input**: `tutorId` in path only, no body

**Output** `200`:
```json
{
  "tutorId":       "uuid",
  "name":          "Alice Smith",
  "imageURL":      "https://...",
  "bio":           "...",
  "averageRating": 4.8,
  "totalReviews":  12,
  "subjects": [
    { "tutorSubjectId": "uuid", "subject": "Mathematics", "academicLevel": "A-Level", "hourlyRate": 35 }
  ],
  "reviews": [
    {
      "review_id":     1712345678000,
      "session_id":    "uuid",
      "tutor_id":      "uuid",
      "student_id":    "uuid",
      "rating":        5,
      "comment":       "Excellent session!",
      "createdAt":     "2026-04-02T10:30:00.000000Z",
      "studentName":   "John Doe",
      "studentAvatar": "https://..."
    }
  ]
}
```

**Errors**: `404` tutor not found · `500` downstream failure

Calls: Tutor → OutSystems → Student (per reviewer)

---

## Deployment

```bash
cd backend
docker-compose up --build -d
```

Local dev gateway (no Docker): `python local_gateway.py`  (runs on port 8000)

---

## Status Summary

| Service | Type | Port | Status |
|---------|------|------|--------|
| Student | Atomic | 5001 | ✅ Active |
| Tutor | Atomic | 5002 | ✅ Active |
| Session | Atomic | 5003 | ✅ Active |
| Payment | Atomic | 5007 | ✅ Active |
| Calendar | Atomic | 5005 | ✅ Active |
| Email | Atomic | 5006 | ⚠️ Placeholder |
| Meeting | Atomic | 5004 | ⚠️ Placeholder |
| Checkout | Composite | 5100 | ✅ Active |
| Process Booking | Composite | 5104 | ✅ Active |
| Create Session | Composite | 5105 | ✅ Active |
| Update Session | Composite | 5106 | ✅ Active |
| Delete Session | Composite | 5107 | ✅ Active |
| Cancel Session | Composite | 5101 | ⚠️ Placeholder |
| Get Sessions | Composite | 5103 | ✅ Active |
| Rate Tutor | Composite | 5102 | ✅ Active |
| Get Tutor | Composite | 5109 | ✅ Active |
