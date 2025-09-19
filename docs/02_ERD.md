```
erDiagram
    User {
        bigint id PK
        string email "varchar(254) UNIQUE NOT NULL CHECK (email = LOWER(email))"
        string username "varchar(100) NOT NULL"
        string password "varchar(128) NOT NULL"
        string nickname "varchar(25), NULL"
        string image_url "varchar(500), NULL"
        string phone_number "varchar(25), NULL"
        boolean is_active "NOT NULL DEFAULT true"
        timestamptz email_verified_at "NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
        timestamptz updated_at "NOT NULL (auto_now)"
        timestamptz deactivated_at "NULL"
    }

    OAuthAccount {
        bigint id PK
        bigint user_id FK "NOT NULL; FK→User.id; ON DELETE CASCADE"
        string provider "varchar(30) NOT NULL CHECK (provider IN ('google','github','kakao','naver'))"
        string subject "varchar(191) NOT NULL"
        string email "varchar(254), NULL"
        boolean email_verified "NOT NULL DEFAULT false"
        text access_token "NULL"
        text refresh_token "NULL"
        timestamptz token_expires_at "NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
        -- UNIQUE(provider, subject)
    }

    Conversation {
        bigint id PK
        bigint owner_id FK "NOT NULL; FK→User.id; ON DELETE CASCADE"
        string title "varchar(200) NOT NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
        timestamptz updated_at "NOT NULL (auto_now)"
    }

    Message {
        bigint id PK
        bigint conversation_id FK "NOT NULL; FK→Conversation.id; ON DELETE CASCADE"
        string role "varchar(10) NOT NULL CHECK (role IN ('user','assistant','system'))" 
        text content "NOT NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
    }

    Dataset {
        bigint id PK
        bigint owner_id FK "NOT NULL; FK→User.id; ON DELETE CASCADE"
        string name "varchar(100) NOT NULL"
        string source "varchar(100), NULL"
        string uri "varchar(500), NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
    }

    PreprocessingJob {
        bigint id PK
        bigint dataset_id FK "NOT NULL; FK→Dataset.id; ON DELETE CASCADE"
        string client_job_id "varchar(64), NULL (멱등키)"
        string status "varchar(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed'))"
        jsonb steps "NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
        timestamptz started_at "NULL"
        timestamptz finished_at "NULL"
        -- UNIQUE(dataset_id, client_job_id) WHERE client_job_id IS NOT NULL
    }

    InferenceRun {
        bigint id PK
        bigint conversation_id FK "NOT NULL; FK→Conversation.id; ON DELETE CASCADE"
        bigint message_id FK "NULL; FK→Message.id; ON DELETE SET NULL"
        string model "varchar(100) NOT NULL"
        integer latency_ms "NOT NULL"
        integer prompt_tokens "NULL"
        integer completion_tokens "NULL"
        string status "varchar(20) NOT NULL DEFAULT 'success' CHECK (status IN ('success','error'))"
        string error_code "varchar(128), NULL"
        text error_message "NULL"
        timestamptz created_at "NOT NULL (auto_now_add)"
    }

    %% --- 관계 ---
    User ||--o{ Conversation : "1:N"
    Conversation ||--o{ Message : "1:N"
    Conversation ||--o{ InferenceRun : "1:N"
    Message ||--o{ InferenceRun : "1:N"
    User ||--o{ Dataset : "1:N"
    Dataset ||--o{ PreprocessingJob : "1:N"
    User ||--o{ OAuthAccount : "1:N"
```