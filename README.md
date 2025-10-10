
# Photo Storage Backend API

This is a Python-based backend application using the FastAPI framework. The application serves as a REST API for managing users, photos, and hashtags, with a strong emphasis on security and modern authentication practices.

## Core Technologies & Architecture

*   **Backend Framework:** **Python 3.10+** with **FastAPI**.
*   **Database:** A relational database (e.g., PostgreSQL) is recommended. The data access layer is managed by an ORM like **SQLAlchemy** with **Alembic** for migrations.
*   **Authentication:** **OAuth 2.0 / OpenID Connect** for user authentication and authorization, implemented using the **Authlib** library.
*   **Data Validation:** **Pydantic** for defining data schemas and validation.
*   **Configuration:** Settings are managed via a library like **Pydantic-settings**. The application supports loading from a `config.yaml` file and from environment variables. **Environment variables have higher priority** and override values from the file.
*   **File Storage:** Any **S3-compatible** object storage (e.g., AWS S3, MinIO, Google Cloud Storage).
*   **Monitoring:** Integration with **Prometheus** for metrics collection. Libraries like `starlette-prometheus` are used.
*   **Asynchronous Operations:** The application is fully asynchronous using `async`/`await` syntax.

## Getting Started

### Prerequisites

*   Python 3.10+
*   A PostgreSQL database
*   An S3-compatible object storage
*   An OpenID Connect (OIDC) provider

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/photo-storage-backend.git
    cd photo-storage-backend
    ```

2.  **Create a virtual environment and install the dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### Configuration

1.  **Rename `config.yaml.example` to `config.yaml`** and update the values with your database, S3, and OIDC provider credentials.

    ```yaml
    database_url: "postgresql://user:password@localhost/photodb"
    s3:
      bucket_name: "photo-storage-bucket"
      aws_access_key_id: "YOUR_AWS_ACCESS_KEY_ID"
      aws_secret_access_key: "YOUR_AWS_SECRET_ACCESS_KEY"
      region_name: "us-east-1"
      # endpoint_url: "http://localhost:9000" # Example for MinIO
    oidc:
      client_id: "YOUR_OIDC_CLIENT_ID"
      client_secret: "YOUR_OIDC_CLIENT_SECRET"
      server_metadata_url: "https://your-oidc-provider.com/.well-known/openid-configuration"
    jwt:
      secret_key: "a-very-secret-key"
      algorithm: "HS256"
      access_token_expire_minutes: 30
    ```

2.  **Configuration can also be provided via environment variables.** Environment variables have higher priority and will override the values from the `config.yaml` file. For nested keys, use a double underscore (`__`) as a delimiter. For example, to set the S3 bucket name, you would use the following environment variable:

    ```bash
    export S3__BUCKET_NAME=my-photo-bucket
    ```

### Database Migrations

Once you have configured your database, you can run the database migrations to create the tables:

```bash
venv/bin/alembic upgrade head
```

### Running the Application

To run the application, use the following command:

```bash
venv/bin/uvicorn src.main:app --reload
```

The application will be available at `http://localhost:8000`.

## API Endpoints

### Monitoring

*   **`GET /health`**
    *   **Description:** A public endpoint to verify that the application is running and responsive.
    *   **Authentication:** Not required.
    *   **Response (200 OK):** `{ "status": "ok" }`
*   **`GET /metrics`**
    *   **Description:** A public endpoint that exposes application metrics in the Prometheus text-based format for scraping.
    *   **Authentication:** Not required.

### Authentication (`/api/v1/auth`)

*   **`GET /api/v1/auth/login`**
    *   **Description:** Initiates the OIDC login process by redirecting the user to the external provider.
*   **`GET /api/v1/auth/callback`**
    *   **Description:** Handles the callback from the OIDC provider after user authentication. Creates the user session and returns a session token.
    *   **Response (200 OK):** `{ "access_token": "your_jwt_token", "token_type": "bearer" }`
*   **`GET /api/v1/auth/me`**
    *   **Description:** Returns information about the currently authenticated user.
    *   **Authentication:** Required.

### Photos (`/api/v1/photos`)

*   **`POST /api/v1/photos/`**
    *   **Description:** Uploads a new photo and associates it with hashtags.
    *   **Authentication:** Required.
    *   **Request:** `multipart/form-data` containing the image file and an optional field for comma-separated hashtags (e.g., `hashtags: "nature, sunset, travel"`).
*   **`GET /api/v1/photos/`**
    *   **Description:** Retrieves a list of photos belonging to the authenticated user. Includes a query parameter for filtering by hashtag.
    *   **Authentication:** Required.
    *   **Query Parameters:** `?hashtag=sunset` (optional).
*   **`GET /api/v1/photos/{photo_id}`**
    *   **Description:** Retrieves a single photo by its ID.
    *   **Authentication:** Required.
*   **`DELETE /api/v1/photos/{photo_id}`**
    *   **Description:** Deletes a photo from the database and the S3 storage.
    *   **Authentication:** Required.

### Hashtags (`/api/v1/hashtags`)

*   **`POST /api/v1/hashtags/`**
    *   **Description:** Creates a new hashtag.
    *   **Authentication:** Required.
    *   **Request Body:** `{ "name": "newhashtag" }`
*   **`GET /api/v1/hashtags/`**
    *   **Description:** Retrieves a list of all existing hashtags.
    *   **Authentication:** Not required.
*   **`GET /api/v1/hashtags/search`**
    *   **Description:** Provides a search endpoint for existing hashtags.
    *   **Authentication:** Not required.
    *   **Query Parameters:** `?q=sun`
