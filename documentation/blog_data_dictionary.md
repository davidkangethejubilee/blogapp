# Blog Data Dictionary

This document describes the blog schema defined in `documentation/blog.dbml`.

## Global notes
- Primary key type: `uuid` (default: `gen_random_uuid()` via `pgcrypto` or `uuid_generate_v4()` via `uuid-ossp`).
- Timestamps: `timestamp` with `created_at` defaulting to `now()`.
- Case-insensitive email: `citext` extension recommended.
- Extensible fields: `jsonb` for `metadata` columns.
- Full-text search: `tsvector` `search` column on `posts` (populate via GENERATED column or trigger) with a `GIN` index.

---

### Table: `users`

Description: Registered users and content authors. Stores authentication details and profile metadata.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| email | citext | NO | --- | UNIQUE | User login / email (case-insensitive) | UNIQUE INDEX |
| password_hash | text | NO | --- | --- | Password hash (bcrypt/argon2 output) | --- |
| display_name | text | YES | --- | --- | Public display name | --- |
| bio | text | YES | --- | --- | Short biography | --- |
| metadata | jsonb | YES | --- | --- | Freeform metadata (user prefs, social links) | GIN index (optional) |
| created_at | timestamp | NO | `now()` | --- | Record creation time | INDEX (optional) |
| updated_at | timestamptz | YES | --- | --- | Last update time | --- |
| deleted_at | timestamptz | YES | --- | --- | Soft-delete timestamp; NULL = active | PARTIAL INDEX recommended |

---

### Table: `categories`

Description: Top-level categories used to group posts by topic.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| name | text | NO | --- | --- | Category display name | --- |
| slug | text | NO | --- | UNIQUE | URL-friendly identifier | UNIQUE INDEX |
| description | text | YES | --- | --- | Optional description | --- |
| created_at | timestamp | NO | `now()` | --- | Creation timestamp | --- |

---

### Table: `posts`

Description: Main blog posts/articles authored by users. Supports drafts, publication, and soft-deletes.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| author_id | uuid | NO | --- | FK → `users.id` | Post author | FK constraint; consider `ON DELETE SET NULL` |
| category_id | uuid | YES | --- | FK → `categories.id` | Optional category | INDEX (optional) |
| title | text | NO | --- | --- | Post title | FULL-TEXT (part of `search`) |
| slug | text | NO | --- | UNIQUE | URL-friendly identifier | UNIQUE INDEX; consider `citext`/lowercase enforcement |
| content | text | YES | --- | --- | Main body content | FULL-TEXT (part of `search`) |
| excerpt | text | YES | --- | --- | Short summary | --- |
| status | varchar(20) | NO | `'draft'` | --- | Workflow state (draft/published/archived) | PARTIAL INDEX (e.g., published) |
| published_at | timestamp | YES | --- | --- | Publication datetime | INDEX (for ordering) |
| metadata | jsonb | YES | --- | --- | Arbitrary post metadata | GIN index (optional) |
| search | tsvector | YES | GENERATED or trigger-populated | --- | Combined tsvector of title+content for full-text search | GIN INDEX (recommended) |
| created_at | timestamp | NO | `now()` | --- | Creation time | INDEX (optional) |
| updated_at | timestamptz | YES | --- | --- | Last update time | --- |
| deleted_at | timestamptz | YES | --- | --- | Soft-delete timestamp | PARTIAL INDEX recommended |

---

### Table: `tags`

Description: Tags for flexible, multi-label classification of posts.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| name | text | NO | --- | --- | Tag display name | --- |
| slug | text | NO | --- | UNIQUE | URL-friendly identifier | UNIQUE INDEX |
| created_at | timestamp | NO | `now()` | --- | Creation time | --- |

---

### Table: `post_tags`

Description: Join table linking `posts` and `tags` (many-to-many).

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| post_id | uuid | NO | --- | FK → `posts.id` | Associated post | FK constraint; index implied by FK |
| tag_id | uuid | NO | --- | FK → `tags.id` | Associated tag | FK constraint; index implied by FK |
| created_at | timestamp | NO | `now()` | --- | Tagging time | --- |

Constraints: composite UNIQUE (`post_id`, `tag_id`) recommended to prevent duplicate tag assignments.

---

### Table: `comments`

Description: User comments on posts; supports nesting via `parent_id` for threaded replies.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| post_id | uuid | NO | --- | FK → `posts.id` | Parent post | INDEX (for retrieval); FK constraint |
| author_id | uuid | YES | --- | FK → `users.id` | Comment author (nullable for anonymous) | INDEX (optional) |
| parent_id | uuid | YES | --- | FK → `comments.id` | Parent comment for threading | --- |
| body | text | NO | --- | --- | Comment content | --- |
| created_at | timestamp | NO | `now()` | --- | Creation time | --- |
| deleted_at | timestamptz | YES | --- | --- | Soft-delete timestamp | PARTIAL INDEX possible |

---

### Table: `attachments`

Description: Media assets (images/files) uploaded and optionally attached to posts.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| post_id | uuid | YES | --- | FK → `posts.id` | Associated post | INDEX; FK constraint |
| uploader_id | uuid | YES | --- | FK → `users.id` | Uploader user | INDEX; FK constraint |
| url | text | NO | --- | --- | Public URL or storage path | --- |
| type | varchar(50) | YES | --- | --- | MIME type or category | --- |
| alt_text | text | YES | --- | --- | Accessibility text | --- |
| metadata | jsonb | YES | --- | --- | Extra attributes (dimensions, variants) | GIN index (optional) |
| created_at | timestamp | NO | `now()` | --- | Upload time | --- |

---

### Table: `revisions`

Description: Historical snapshots of posts for audit and rollback.

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| post_id | uuid | NO | --- | FK → `posts.id` | Post being revised | INDEX; FK constraint |
| editor_id | uuid | YES | --- | FK → `users.id` | Editor who made the revision | --- |
| title | text | YES | --- | --- | Title at revision | --- |
| content | text | YES | --- | --- | Content at revision | --- |
| created_at | timestamp | NO | `now()` | --- | Revision timestamp | --- |

---

### Table: `likes`

Description: Likes for posts or comments; implemented as a polymorphic target (by `target_type`).

| Column | Type | Null? | Default | Key | Description | Index / Constraint |
|---|---|---:|---|---|---|---|
| id | uuid | NO | `gen_random_uuid()` | PK | Primary key | --- |
| user_id | uuid | NO | --- | FK → `users.id` | Liking user | INDEX; FK constraint |
| target_type | varchar(50) | NO | --- | --- | Entity type being liked (`post` or `comment`) | --- |
| target_id | uuid | NO | --- | --- | ID of liked entity | INDEX; if polymorphic, enforce via application logic or DB CHECKs |
| created_at | timestamp | NO | `now()` | --- | Like timestamp | --- |

Constraints: consider UNIQUE (`user_id`, `target_type`, `target_id`) to prevent duplicate likes.

---


## Implementation checklist (Postgres)

- Enable extensions prior to creating tables: `CREATE EXTENSION IF NOT EXISTS citext; CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE EXTENSION IF NOT EXISTS pg_trgm;`
- Create `posts.search` as a `GENERATED ALWAYS AS (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, '')) ) STORED` or maintain via trigger on insert/update.
- Create GIN index on `posts.search`: `CREATE INDEX ON posts USING GIN(search);`
- Create GIN index on `metadata` if you plan to query json fields heavily: `CREATE INDEX ON posts USING GIN(metadata);`
- Create unique and partial indexes as noted above.

## Next steps

- Create `documentation/blog.sql` with runnable DDL (extensions, table DDL, indexes, triggers). If you want, I can generate that file next.

