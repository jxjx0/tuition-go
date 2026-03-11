# Get Sessions Composite Service

## Overview

The **Get Sessions** composite service is an orchestrator that aggregates data from multiple backend services to provide enriched session information. It acts as a bridge between the Session Service and Tutor Service, combining session details with comprehensive tutor information in a single API response.

## Purpose

This composite service solves the problem of data fragmentation across microservices. When clients need session information along with tutor details (name, image, academic level), they would typically need to:

1. Call the Session Service to get session data
2. Parse the session data to extract tutor IDs
3. Separately call the Tutor Service for each tutor to get their details
4. Manually combine the responses

The Get Sessions service **eliminates this complexity** by:
- Orchestrating calls to multiple backend services
- Enriching session data with tutor information automatically
- Returning complete, ready-to-use session objects
- Reducing client-side logic and network calls

## Architecture

### Service Dependencies
- **Session Service** (http://session:5003) - Source of session records
- **Tutor Service** (http://tutor:5002) - Source of tutor details and subject information

### Data Flow
```
Client Request
    ↓
Get Sessions Service
    ├─→ Fetch sessions from Session Service
    ├─→ For each session, fetch tutor details from Tutor Service
    ├─→ Fetch tutor subjects/academic levels from Tutor Service
    └─→ Combine and enrich session data
    ↓
Return enriched session objects to client
```

## Endpoints

### 1. Get Student Sessions
**GET** `/student/{studentId}/sessions`

Returns all sessions for a specific student, enriched with tutor information.

**Response Example:**
```json
[
        {
        "sessionId": "afbd5ad4-a162-434b-8b64-b66b685a05b0",
        "tutorId": "1354994b-6589-421e-bb5f-8f0a59a1b29b",
        "studentId": "5e97eb66-5fd9-4235-b9c7-788b770ef42a",
        "tutorSubjectId": "d964fe8b-f4d6-4eb2-94f5-3d00bf0eda65",
        "startTime": "2026-03-05T06:00:00+00:00",
        "endTime": "2026-03-05T15:00:00",
        "status": "completed",
        "durationMins": 60.0,
        "meetingLink": "https://meet.google.com/abc-defg-hij",
        "createdAt": "2026-03-11T14:19:50.764533",
        "updatedAt": "2026-03-11T14:19:50.764533",
        "tutorName": "Dick Lee",
        "tutorImageUrl": "https://mbywmrfzaurxucjnjnjb.supabase.co/storage/v1/object/public/tuitiongo/1354994b-6589-421e-bb5f-8f0a59a1b29b/174c49c2-7b64-43ed-801d-ec35cfff3e11.png",
        "subjectName": "Science",
        "academicLevel": "Secondary 1",
        "totalPrice": 35.0
    }
]
```

### 2. Get Tutor Sessions

Basically get  tutor sessions by tutorid with the student info

Still in progress, waiting for student atomic service to complete first

## API Gateway Integration

This service is exposed through Kong API Gateway at:
```
GET /api/v1/getsessions/student/{studentId}/sessions
-> http://localhost:8000/api/v1/getsessions/student/5e97eb66-5fd9-4235-b9c7-788b770ef42a/sessions

GET /api/v1/getsessions/session/{sessionId}
-> http://localhost:8000/api/v1/getsessions/session/a5c851b5-ac19-47ae-9baf-c7b95873d23c
```

All routes strip the `/api/v1/getsessions/` prefix and forward to this service on port 5103.
