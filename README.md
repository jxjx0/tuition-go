# TuitionGo

TuitionGo is a marketplace platform that connects students with tutors for private tuition sessions. Students can browse and book tutors, pay securely, manage upcoming sessions, and leave reviews — all in one place. Tutors can list their availability, manage their schedule, and get paid automatically. The platform handles the full session lifecycle: from discovery and checkout through calendar sync, email notifications, and post-session ratings.

---

## Tech Stack

**Frontend**

<p>
  <img src="https://skillicons.dev/icons?i=vue,ts,vite,tailwind" height="40" />
  <img src="https://cdn.simpleicons.org/radixui/161618" height="40" title="Radix Vue" />
</p>
<p>
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/Radix_Vue-161618?style=for-the-badge&logo=radixui&logoColor=white" />
</p>

**Backend**

<p>
  <img src="https://skillicons.dev/icons?i=python,flask" height="40" />
</p>
<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
</p>

**Infrastructure**

<p>
  <img src="https://skillicons.dev/icons?i=docker,rabbitmq" height="40" />
  <img src="https://cdn.simpleicons.org/kong/003459" height="40" title="Kong Gateway" />
</p>
<p>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" />
  <img src="https://img.shields.io/badge/Kong_Gateway-003459?style=for-the-badge&logo=kong&logoColor=white" />
</p>

**Authentication & Database**

<p>
  <img src="https://skillicons.dev/icons?i=supabase" height="40" />
  <img src="https://cdn.simpleicons.org/clerk/6C47FF" height="40" title="Clerk" />
</p>
<p>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Clerk-6C47FF?style=for-the-badge&logo=clerk&logoColor=white" />
</p>

**External Services**

<p>
  <img src="https://cdn.simpleicons.org/stripe/635BFF" height="40" title="Stripe" />
  <img src="https://cdn.simpleicons.org/googlecalendar/4285F4" height="40" title="Google Calendar" />
  <img src="outsystems_logo.png" height="40" title="OutSystems" />
</p>
<p>
  <img src="https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Calendar-4285F4?style=for-the-badge&logo=googlecalendar&logoColor=white" />
  <img src="https://img.shields.io/badge/OutSystems-FF4F00?style=for-the-badge&logo=outsystems&logoColor=white" />
</p>

---

## Architecture Overview

TuitionGo follows a microservices architecture split into two layers: **atomic services** (single-responsibility data services) and **composite services** (orchestrators that coordinate multiple atomic services to fulfill a business operation).

All traffic from the frontend is routed through a **Kong API Gateway**, which handles routing and plugin-based auth. Async communication between services (e.g. email notifications) is handled via **RabbitMQ**.

```
Frontend (Vue 3)
     │
     ▼
Kong API Gateway (:8000)
     │
     ├──► Atomic Services
     │         student (:5001)
     │         tutor (:5002)
     │         session (:5003)
     │         calendar (:5005)  ──► Google Calendar API
     │         email (:5006)     ◄── RabbitMQ
     │         payment (:5007)   ──► Stripe
     │
     └──► Composite Services
               checkout (:5100)
               cancel-session (:5101)
               rate-tutor (:5102)
               get-sessions (:5103)
               process-booking (:5104)
               create-session (:5105)
               update-session (:5106)
               delete-session (:5107)
               complete-session (:5108)
               get-tutor (:5109)
```

---

## Atomic Services

Atomic services own a single domain and expose CRUD operations against Supabase. They do not call other services.

| Service | Port | Responsibility |
|---|---|---|
| **student** | 5001 | Student profiles and account management |
| **tutor** | 5002 | Tutor profiles, subjects, and ratings |
| **session** | 5003 | Session records and availability slots |
| **calendar** | 5005 | Google Calendar event management |
| **email** | 5006 | Email dispatch via RabbitMQ consumer |
| **payment** | 5007 | Stripe checkout session creation and webhook handling |

---

## Composite Services

Composite services orchestrate multiple atomic services to execute a complete business workflow.

| Service | Port | What it does |
|---|---|---|
| **checkout** | 5100 | Validates session and tutor, then calls payment service to generate a Stripe checkout URL |
| **cancel-session** | 5101 | Cancels a session, refunds the student via Stripe, removes calendar event, and sends notification emails via RabbitMQ |
| **rate-tutor** | 5102 | Validates the completed session, submits a review to OutSystems, and updates the tutor's average rating |
| **get-sessions** | 5103 | Fetches enriched session lists (with tutor and student details) for dashboard views |
| **process-booking** | 5104 | Confirms a booking after successful Stripe payment: updates session status, creates calendar events for both parties, and sends confirmation emails via RabbitMQ |
| **create-session** | 5105 | Creates a new session slot and a corresponding Google Calendar event |
| **update-session** | 5106 | Updates session details and syncs changes to Google Calendar |
| **delete-session** | 5107 | Deletes a session and its associated calendar event |
| **complete-session** | 5108 | Marks a session as completed and sends post-session emails via RabbitMQ |
| **get-tutor** | 5109 | Returns a tutor's profile enriched with reviews from OutSystems |

---

## Project Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) (v18+) and [pnpm](https://pnpm.io/)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/tuition-go.git
cd tuition-go
```

### 2. Configure environment variables

Create a `.env` file inside `backend/`:

```bash
cp backend/.env.example backend/.env
```

Fill in the required values:

```env
# Clerk
CLERK_SECRET_KEY=

# Supabase
SUPABASE_URL=
SUPABASE_KEY=

# Stripe
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
```

### 3. Start the backend

```bash
cd backend
docker compose up --build kong
```

This starts all atomic and composite services, Kong API Gateway, and RabbitMQ. Kong Admin UI is available at `http://localhost:8002`.

### 4. Configure frontend environment variables

Create a `.env.local` file inside `frontend/tuition-go/`:

```bash
cp frontend/tuition-go/.env.local.example frontend/tuition-go/.env.local
```

Fill in the required values:

```env
# Clerk (get this from your Clerk dashboard → API Keys)
VITE_CLERK_PUBLISHABLE_KEY=
```

### 5. Start the frontend

```bash
cd frontend/tuition-go
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Service Ports Reference

| Service | Port |
|---|---|
| Kong Proxy | 8000 |
| Kong Admin API | 8001 |
| Kong Admin GUI | 8002 |
| RabbitMQ AMQP | 5672 |
| RabbitMQ Management UI | 15672 |
| student | 5001 |
| tutor | 5002 |
| session | 5003 |
| calendar | 5005 |
| email | 5006 |
| payment | 5007 |
| checkout | 5100 |
| cancel-session | 5101 |
| rate-tutor | 5102 |
| get-sessions | 5103 |
| process-booking | 5104 |
| create-session | 5105 |
| update-session | 5106 |
| delete-session | 5107 |
| complete-session | 5108 |
| get-tutor | 5109 |

Each service exposes Swagger docs at `http://localhost:<port>/docs`.
