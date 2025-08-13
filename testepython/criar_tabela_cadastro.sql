-- Script para criar a tabela cadastro
-- Execute este script no phpMyAdmin do XAMPP

USE testepython;

-- Criar a tabela cadastro com apenas as colunas necessárias
CREATE TABLE IF NOT EXISTS cadastro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(20)
);

-- Verificar se a tabela foi criada
DESCRIBE cadastro;
