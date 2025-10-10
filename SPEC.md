# Project Specification: Photo Storage Backend API

This document outlines the technical requirements for a Python-based backend application using the **FastAPI** framework. The application will serve as a REST API for managing users, photos, and hashtags, with a strong emphasis on security and modern authentication practices.

---

### 1. Core Technologies & Architecture

* **Backend Framework:** **Python 3.10+** with **FastAPI**.
* **Database:** A relational database (e.g., PostgreSQL) is recommended. The data access layer should be managed by an ORM like **SQLAlchemy** with **Alembic** for migrations.
* **Authentication:** **OAuth 2.0 / OpenID Connect** for user authentication and authorization, implemented using the **Authlib** library.
* **Data Validation:** **Pydantic** for defining data schemas and validation.
* **Configuration:** Settings are managed via a library like **Pydantic-settings**. The application must support loading from a `config.yaml` file and from environment variables. **Environment variables have higher priority** and override values from the file.
* **File Storage:** Any **S3-compatible** object storage (e.g., AWS S3, MinIO, Google Cloud Storage).
* **Monitoring:** Integration with **Prometheus** for metrics collection. Libraries like `starlette-prometheus` can be used.
* **Asynchronous Operations:** The application should be fully asynchronous using `async`/`await` syntax.

---

### 2. Database Schema

The database will consist of three primary tables and one association table for the many-to-many relationship.

#### `users` Table

Stores user information. Registration is handled externally, so this table will store a reference to the user's identity from the external provider.

* `id` (Integer, Primary Key, Auto-increment)
* `external_id` (String, Unique, Not Null): The unique subject identifier (`sub`) from the OIDC provider.
* `username` (String, Unique, Not Null): The username or email from the OIDC provider.
* `created_at` (DateTime, Default: now)

#### `photos` Table

Stores metadata for each uploaded photo.

* `id` (Integer, Primary Key, Auto-increment)
* `owner_id` (Integer, Foreign Key to `users.id`, Not Null)
* `public_url` (String, Not Null): The public URL to the photo file in the S3 storage.
* `s3_key` (String, Not Null): The unique key (UUID) of the file in the S3 bucket.
* `created_at` (DateTime, Default: now)

#### `hashtags` Table

Stores unique hashtag names.

* `id` (Integer, Primary Key, Auto-increment)
* `name` (String, Unique, Not Null): The hashtag text (e.g., "sunset", "travel"). Stored in lowercase to ensure uniqueness.

#### `photo_hashtags` Association Table

A pivot table to create a many-to-many relationship between photos and hashtags.

* `photo_id` (Integer, Foreign Key to `photos.id`, Primary Key)
* `hashtag_id` (Integer, Foreign Key to `hashtags.id`, Primary Key)

---

### 3. Authentication and Authorization

* **External Provider Integration:** Use **Authlib** to integrate with an OpenID Connect / OAuth 2.0 provider (e.g., Google, Okta, Auth0). The system will rely on the provider for the authentication process.
* **Login Flow:**
    1.  A user initiates login via a `/auth/login` endpoint.
    2.  The application redirects the user to the external provider's authorization page.
    3.  After successful login, the provider redirects the user back to a `/auth/callback` endpoint in our application with an authorization code.
    4.  The application exchanges the code for an access token and user information.
    5.  It checks if a user with the provider's `sub` (subject) identifier exists in the `users` table. If not, it creates a new user record.
    6.  The application generates its own session token (e.g., a JWT) and returns it to the client.
* **User Registration:** There is **no self-registration endpoint**. User accounts must be pre-registered by an administrator directly within the external identity provider's system. When an admin-approved user logs in for the first time, their account will be automatically created in the application's database.
* **Authorization:**
    * All endpoints that manage photos (`/photos/*`) must be protected and require a valid session token.
    * Business logic must enforce that a user can **only view, update, or delete their own photos**. Accessing another user's photos must be strictly forbidden, resulting in a `403 Forbidden` or `404 Not Found` error.

---

### 4. S3-Compatible File Storage

* **Upload Process:**
    1.  The user sends a `POST` request with the image file to the `/photos/` endpoint.
    2.  The backend generates a **Version 4 UUID** (e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479.jpg`) to be used as the filename (key) in the S3 bucket. This prevents enumeration attacks and filename collisions.
    3.  The application uploads the file stream directly to the S3 bucket using the generated UUID as the key.
    4.  Upon successful upload, the application constructs the public URL for the stored object.
    5.  This public URL and the UUID key are saved in the `photos` table in the database.

---

### 5. API Endpoints (REST Specification)

#### Monitoring

* **`GET /health`**
    * **Description:** A public endpoint to verify that the application is running and responsive. Used by monitoring services and load balancers.
    * **Authentication:** Not required.
    * **Response (200 OK):** `{ "status": "ok" }`
* **`GET /metrics`**
    * **Description:** A public endpoint that exposes application metrics in the Prometheus text-based format for scraping.
    * **Authentication:** Not required.
    * **Response (200 OK):** A `text/plain` response with metrics.
        ```
        # HELP http_requests_latency_seconds HTTP request latency
        # TYPE http_requests_latency_seconds histogram
        http_requests_latency_seconds_bucket{method="GET",path="/api/v1/photos/",le="0.05"} 1
        ...
        # HELP http_requests_total Total number of HTTP requests
        # TYPE http_requests_total counter
        http_requests_total{method="GET",path="/api/v1/photos/",status_code="200"} 5
        ...
        ```

#### Authentication (`/api/v1/auth`)

* **`GET /api/v1/auth/login`**
    * **Description:** Initiates the OIDC login process by redirecting the user to the external provider.
    * **Response:** `307 Temporary Redirect`.
* **`GET /api/v1/auth/callback`**
    * **Description:** Handles the callback from the OIDC provider after user authentication. Creates the user session and returns a session token.
    * **Response (200 OK):** `{ "access_token": "your_jwt_token", "token_type": "bearer" }`
* **`GET /api/v1/auth/me`**
    * **Description:** Returns information about the currently authenticated user.
    * **Authentication:** Required.
    * **Response (200 OK):** `{ "id": 1, "username": "user@example.com" }`

#### Photos (`/api/v1/photos`)

* **`POST /api/v1/photos/`**
    * **Description:** Uploads a new photo and associates it with hashtags.
    * **Authentication:** Required.
    * **Request:** `multipart/form-data` containing the image file and an optional field for comma-separated hashtags (e.g., `hashtags: "nature, sunset, travel"`).
    * **Response (201 Created):** The created photo object `{ "id": 123, "public_url": "...", "hashtags": [{"name": "nature"}, ...] }`
* **`GET /api/v1/photos/`**
    * **Description:** Retrieves a list of photos belonging to the authenticated user. Includes a query parameter for filtering by hashtag.
    * **Authentication:** Required.
    * **Query Parameters:** `?hashtag=sunset` (optional).
    * **Response (200 OK):** A list of photo objects. `[ { "id": 123, "public_url": "...", ... }, ... ]`
* **`GET /api/v1/photos/{photo_id}`**
    * **Description:** Retrieves a single photo by its ID.
    * **Authentication:** Required.
    * **Permissions:** The photo must belong to the authenticated user.
    * **Response (200 OK):** A single photo object.
    * **Error Response (404 Not Found):** If the photo does not exist or does not belong to the user.
* **`DELETE /api/v1/photos/{photo_id}`**
    * **Description:** Deletes a photo from the database and the S3 storage.
    * **Authentication:** Required.
    * **Permissions:** The photo must belong to the authenticated user.
    * **Response (204 No Content):** On successful deletion.
    * **Error Response (404 Not Found):** If the photo does not exist or does not belong to the user.

#### Hashtags (`/api/v1/hashtags`)

* **`POST /api/v1/hashtags/`**
    * **Description:** Creates a new hashtag.
    * **Authentication:** Required.
    * **Request Body:** `{ "name": "newhashtag" }`
    * **Response (201 Created):** `{ "id": 10, "name": "newhashtag" }`
    * **Error Response (409 Conflict):** If a hashtag with that name already exists.
* **`GET /api/v1/hashtags/`**
    * **Description:** Retrieves a list of all existing hashtags.
    * **Authentication:** Not required.
    * **Response (200 OK):** `[ {"id": 1, "name": "sunset"}, {"id": 2, "name": "travel"} ]`
* **`GET /api/v1/hashtags/search`**
    * **Description:** Provides a search endpoint for existing hashtags, useful for autocomplete features on the client-side.
    * **Authentication:** Not required.
    * **Query Parameters:** `?q=sun`
    * **Response (200 OK):** `[ {"id": 1, "name": "sunset"}, {"id": 5, "name": "sunny"} ]`

---

### 6. Configuration Management

All configuration parameters (database credentials, S3 keys, OIDC provider details, etc.) should be managed through a centralized Pydantic `Settings` class.

* **Loading Priority:** The application will load configuration in the following order, with later sources overriding earlier ones:
    1.  **Default values** defined in the Pydantic settings model code (lowest priority).
    2.  Values from a **`config.yaml`** file.
    3.  Values from **environment variables** (highest priority).

* **Example:**
    * A `DATABASE_URL` can be defined in `config.yaml`.
    * If the `DATABASE_URL` environment variable is also set, its value will be used instead of the one from the file.