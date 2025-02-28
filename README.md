## Project Structure

- `automobile_service/`: A Django-based service managing automobile-related data.
- `email_service/`: A Django-based service handling email functionalities.

## API Documentation

Interactive API documentation is available via Swagger UI. It can be found at `http://localhost:8000/api/schema/swagger-ui/`

## Installation
### Prerequisites

- Make sure you have [Docker](https://docs.docker.com/get-started/get-docker/) installed on your machine.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/hanane-yh/4FPA5-72521
   ```
2. Navigate to the project directory.
3. Build and start the  Docker containers:
   ```bash
   docker compose up -d --build
    ```


## Note

- The `.env.sample` files in both `automobile_service/` and `email_service/` directories provide a template for environment variables required by each service. Copy these files to `.env` and adjust the values as needed.
