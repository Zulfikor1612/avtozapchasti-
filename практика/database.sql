-- База данных «Учет продаж автозапчастей»
-- Выполнить этот скрипт в MySQL Workbench перед запуском приложения

CREATE DATABASE IF NOT EXISTS avtozapchasti
    DEFAULT CHARACTER SET utf8mb4;

USE avtozapchasti;

-- Таблица клиентов
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- Таблица автозапчастей
CREATE TABLE IF NOT EXISTS parts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock INT NOT NULL CHECK (stock >= 0)
);

-- Таблица продаж
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    total DECIMAL(10,2) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- Начальное заполнение
INSERT INTO clients (full_name, phone) VALUES
('Иванов Иван Иванович', '+7-900-111-22-33'),
('Петрова Анна Сергеевна', '+7-900-444-55-66'),
('Сидоров Петр Николаевич', '+7-900-777-88-99');

INSERT INTO parts (article, name, price, stock) VALUES
('A-001', 'Масляный фильтр', 450.00, 20),
('A-002', 'Тормозные колодки', 2500.00, 10),
('A-003', 'Свеча зажигания', 320.50, 50),
('B-001', 'Воздушный фильтр', 680.00, 15);
