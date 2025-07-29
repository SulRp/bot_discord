-- Tabela de Advertências
CREATE TABLE IF NOT EXISTS advertencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    motivo TEXT NOT NULL,
    observacao TEXT,
    tipo VARCHAR(10) NOT NULL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    validade DATETIME DEFAULT NULL,
    removida BOOLEAN DEFAULT FALSE
);

-- Tabela de Pontos (registro de ponto por staff)
CREATE TABLE IF NOT EXISTS pontos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    inicio DATETIME DEFAULT NULL,
    pausado DATETIME DEFAULT NULL,
    retomado DATETIME DEFAULT NULL,
    fim DATETIME DEFAULT NULL,
    total_segundos INT DEFAULT 0,
    INDEX(user_id)
);

-- Tabela de Tickets (registro de tickets abertos)
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    canal_id BIGINT DEFAULT NULL,
    INDEX(user_id)
);
