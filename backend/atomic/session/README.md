# Session Service

This is the session atomic service.

## Environment Variables

This service requires a `.env` file for Supabase configuration.

### Docker
When running the service with `docker-compose up`, the configuration is handled by the `env_file` property in the `docker-compose.yml` file.

## Instructions
Create a `.env` file in this directory (`backend/atomic/session`). The `docker-compose.yml` is configured to load this file.

The `.env` file should contain the following variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Replace `your_supabase_url` and `your_supabase_key` with your actual Supabase project URL and API key.

Let me know if you need the keys! Should be able to find in Supabase!

## Testing

Once the service is running, the API documentation is available in your browser through Swagger UI.

Navigate to: `http://localhost:5003/docs`
