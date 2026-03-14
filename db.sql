-- USERS
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),
    github_id       VARCHAR(100) UNIQUE,
    github_username VARCHAR(100),
    timezone        VARCHAR(50) NOT NULL DEFAULT 'UTC',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PROJECTS
CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    color           VARCHAR(7),
    status          VARCHAR(20) DEFAULT 'active',  -- active, archived, on_hold
    weekly_goal_hours DECIMAL(4,2),
    github_repo     VARCHAR(255),                  -- linked repo for webhooks
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SESSIONS
CREATE TABLE sessions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id        UUID REFERENCES projects(id) ON DELETE SET NULL,
    energy_start      SMALLINT CHECK (energy_start BETWEEN 1 AND 10),
    energy_end        SMALLINT CHECK (energy_end BETWEEN 1 AND 10),
    mood              VARCHAR(20),                 -- great, good, neutral, bad, terrible
    flow_achieved     BOOLEAN DEFAULT FALSE,
    notes             TEXT,
    blockers          TEXT,
    started_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at          TIMESTAMP WITH TIME ZONE,
    duration_minutes  INTEGER,                     -- computed on close
    status            VARCHAR(20) DEFAULT 'open',  -- open, closed, abandoned
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- COMMITS
CREATE TABLE commits (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id    UUID REFERENCES sessions(id) ON DELETE SET NULL,
    project_id    UUID REFERENCES projects(id) ON DELETE SET NULL,
    sha           VARCHAR(40) UNIQUE NOT NULL,
    message       TEXT NOT NULL,
    repo_name     VARCHAR(255) NOT NULL,
    additions     INTEGER DEFAULT 0,
    deletions     INTEGER DEFAULT 0,
    committed_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- STREAKS
CREATE TABLE streaks (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_streak    INTEGER DEFAULT 0,
    longest_streak    INTEGER DEFAULT 0,
    last_active_date  DATE,
    freeze_used       BOOLEAN DEFAULT FALSE,
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- INSIGHTS
CREATE TABLE insights (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id   UUID REFERENCES projects(id) ON DELETE CASCADE,
    type         VARCHAR(50) NOT NULL,   -- peak_hour, avg_flow_time, best_day, top_project
    value        JSONB NOT NULL,         -- flexible payload per insight type
    computed_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- DIGESTS
CREATE TABLE digests (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_start  DATE NOT NULL,
    period_end    DATE NOT NULL,
    content       JSONB NOT NULL,        -- full snapshot, never mutated after creation
    delivered_at  TIMESTAMP WITH TIME ZONE,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- INDEXES
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_project_id ON sessions(project_id);
CREATE INDEX idx_sessions_started_at ON sessions(started_at);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_commits_session_id ON commits(session_id);
CREATE INDEX idx_commits_user_id ON commits(user_id);
CREATE INDEX idx_commits_committed_at ON commits(committed_at);
CREATE INDEX idx_insights_user_id ON insights(user_id);
CREATE INDEX idx_insights_type ON insights(type);
CREATE INDEX idx_digests_user_id ON digests(user_id);