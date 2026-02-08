BEGIN;

-- Tabla de casos de soporte
CREATE TABLE support_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    case_type VARCHAR(20) NOT NULL CHECK (case_type IN ('support', 'requirement', 'investigation')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices para support_cases
CREATE INDEX idx_support_cases_status ON support_cases(status);
CREATE INDEX idx_support_cases_priority ON support_cases(priority);
CREATE INDEX idx_support_cases_type ON support_cases(case_type);
CREATE INDEX idx_support_cases_created_by ON support_cases(created_by);
CREATE INDEX idx_support_cases_created_at ON support_cases(created_at DESC);
CREATE INDEX idx_support_cases_title_search ON support_cases USING gin(to_tsvector('spanish', title));
CREATE INDEX idx_support_cases_status_priority ON support_cases(status, priority);

-- Tabla de consultas SQL ejecutadas
CREATE TABLE case_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES support_cases(id) ON DELETE CASCADE,
    database_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    execution_time_ms INTEGER,
    rows_affected INTEGER,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    executed_by VARCHAR(255) NOT NULL
);

-- Índices para case_queries
CREATE INDEX idx_case_queries_case_id ON case_queries(case_id);
CREATE INDEX idx_case_queries_executed_at ON case_queries(executed_at DESC);
CREATE INDEX idx_case_queries_executed_by ON case_queries(executed_by);

COMMIT;
