"""Database initialization SQL"""

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(255) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    tags VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_reviewed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id VARCHAR(36) PRIMARY KEY,
    ticket_id VARCHAR(100) NOT NULL UNIQUE,
    article_id VARCHAR(36) REFERENCES articles(id),
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create audit_results table
CREATE TABLE IF NOT EXISTS audit_results (
    id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(36) NOT NULL REFERENCES articles(id),
    freshness_score FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    article_age_days INTEGER NOT NULL,
    ticket_count INTEGER DEFAULT 0 NOT NULL,
    days_since_last_update INTEGER NOT NULL,
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create ai_recommendations table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(36) NOT NULL REFERENCES articles(id),
    recommendation_type VARCHAR(50) NOT NULL,
    original_content TEXT NOT NULL,
    recommended_content TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create audit_jobs table
CREATE TABLE IF NOT EXISTS audit_jobs (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    total_articles INTEGER DEFAULT 0,
    processed_articles INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_articles_active ON articles(is_active);
CREATE INDEX IF NOT EXISTS idx_tickets_article_id ON tickets(article_id);
CREATE INDEX IF NOT EXISTS idx_audit_results_article_id ON audit_results(article_id);
CREATE INDEX IF NOT EXISTS idx_audit_results_status ON audit_results(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_article_id ON ai_recommendations(article_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_accepted ON ai_recommendations(accepted, rejected);
CREATE INDEX IF NOT EXISTS idx_audit_jobs_status ON audit_jobs(status);
