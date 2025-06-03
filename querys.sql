

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('doador', 'hemocentro') NOT NULL,
    pontos INT DEFAULT 0,
    nivel INT DEFAULT 1,
    tipo_sanguineo VARCHAR(3),
    data_nascimento DATE,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20),
    endereco VARCHAR(200),
    cep VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    foto_perfil VARCHAR(255),
    verificado BOOLEAN DEFAULT FALSE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_tipo (tipo)
);


CREATE TABLE IF NOT EXISTS hemocentros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    horario_funcionamento VARCHAR(100),
    responsavel VARCHAR(100),
    cnpj VARCHAR(18) UNIQUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hemocentro_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hemocentro_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (hemocentro_id) REFERENCES hemocentros(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    hemocentro_id INT NOT NULL,
    data_agendamento DATE NOT NULL,
    horario TIME NOT NULL,
    status ENUM('Agendado', 'Concluído', 'Cancelado') DEFAULT 'Agendado',
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (hemocentro_id) REFERENCES hemocentros(id)
);


CREATE TABLE IF NOT EXISTS conquistas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    pontos INT NOT NULL,
    icone VARCHAR(10),
    requisito VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS usuario_conquistas (
    usuario_id INT NOT NULL,
    conquista_id INT NOT NULL,
    data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, conquista_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (conquista_id) REFERENCES conquistas(id)
);


CREATE TABLE IF NOT EXISTS campanhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hemocentro_id INT,
    titulo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    urgencia ENUM('Baixa', 'Média', 'Alta') NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    ativa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (hemocentro_id) REFERENCES hemocentros(id)
);


CREATE TABLE IF NOT EXISTS estoque_sangue (
    hemocentro_id INT NOT NULL,
    tipo_sanguineo VARCHAR(3) NOT NULL,
    quantidade INT NOT NULL,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (hemocentro_id, tipo_sanguineo),
    FOREIGN KEY (hemocentro_id) REFERENCES hemocentros(id)
);


-- Inserções adicionais de usuários (doadores)
INSERT INTO usuarios (nome, email, senha, tipo, tipo_sanguineo, data_nascimento, cpf, telefone, endereco, cep, cidade, estado, pontos, nivel) VALUES
-- Doador Luiz (conta principal)
('Luiz', 'email@email.com', SHA2('11', 256), 'doador', 'B+', '1995-03-10', '456.189.123-45', '(41) 97777-3333', 'Rua dos Coqueiros, 300', '88100-000', 'Curitiba', 'PR', 230, 3),
('Luiz', 'mail@email.com', SHA2('22', 256), 'hemocentro', NULL, NULL, NULL, '(41) 97777-3333', 'Rua dos Coqueiros, 300', NULL, NULL, NULL, NULL, NULL),

-- Outros doadores (20 registros)
('Ana Carolina', 'ana.carolina@email.com', SHA2('senha123', 256), 'doador', 'A+', '1992-07-15', '111.222.333-44', '(48) 91111-1111', 'Rua das Palmeiras, 50', '88015-000', 'Florianópolis', 'SC', 150, 2),
('Pedro Henrique', 'pedro.h@email.com', SHA2('senha123', 256), 'doador', 'O+', '1988-11-22', '222.333.444-55', '(48) 92222-2222', 'Av. Central, 200', '88020-100', 'São José', 'SC', 80, 1),
('Mariana Santos', 'mariana.s@email.com', SHA2('senha123', 256), 'doador', 'AB-', '1990-05-30', '333.444.555-66', '(48) 93333-3333', 'Travessa das Flores, 30', '88025-200', 'Palhoça', 'SC', 320, 4),
('Ricardo Oliveira', 'ricardo.o@email.com', SHA2('senha123', 256), 'doador', 'B-', '1985-09-18', '444.555.666-77', '(48) 94444-4444', 'Rua dos Pássaros, 100', '88030-300', 'Biguaçu', 'SC', 50, 1),
('Fernanda Lima', 'fernanda.l@email.com', SHA2('senha123', 256), 'doador', 'A-', '1993-02-25', '555.666.777-88', '(48) 95555-5555', 'Alameda das Árvores, 250', '88035-400', 'Florianópolis', 'SC', 180, 2),
('Gustavo Pereira', 'gustavo.p@email.com', SHA2('senha123', 256), 'doador', 'O-', '1987-12-05', '666.777.888-99', '(48) 96666-6666', 'Praça Central, 70', '88040-500', 'São José', 'SC', 270, 3),
('Juliana Costa', 'juliana.c@email.com', SHA2('senha123', 256), 'doador', 'AB+', '1991-04-12', '777.888.999-00', '(48) 97777-7777', 'Rua das Pedras, 120', '88045-600', 'Palhoça', 'SC', 90, 1),
('Lucas Martins', 'lucas.m@email.com', SHA2('senha123', 256), 'doador', 'B+', '1994-08-08', '888.999.000-11', '(48) 98888-8888', 'Av. Beira Rio, 300', '88050-700', 'Florianópolis', 'SC', 400, 5),
('Camila Rocha', 'camila.r@email.com', SHA2('senha123', 256), 'doador', 'A+', '1989-06-20', '999.000.111-22', '(48) 99999-9999', 'Travessa do Sol, 80', '88055-800', 'São José', 'SC', 120, 2),
('Diego Almeida', 'diego.a@email.com', SHA2('senha123', 256), 'doador', 'O+', '1996-01-15', '000.111.222-33', '(48) 90000-0000', 'Rua da Lua, 150', '88060-900', 'Palhoça', 'SC', 60, 1),
('Patrícia Nunes', 'patricia.n@email.com', SHA2('senha123', 256), 'doador', 'B-', '1990-10-10', '123.123.123-12', '(48) 91234-5678', 'Alameda dos Coqueiros, 90', '88065-000', 'Florianópolis', 'SC', 210, 3),
('Roberto Silva', 'roberto.s@email.com', SHA2('senha123', 256), 'doador', 'A-', '1986-03-28', '234.234.234-23', '(48) 92345-6789', 'Praça das Árvores, 40', '88070-100', 'São José', 'SC', 340, 4),
('Tatiane Oliveira', 'tatiane.o@email.com', SHA2('senha123', 256), 'doador', 'AB-', '1992-07-07', '345.345.345-34', '(48) 93456-7890', 'Rua das Estrelas, 60', '88075-200', 'Palhoça', 'SC', 70, 1),
('Vinícius Costa', 'vinicius.c@email.com', SHA2('senha123', 256), 'doador', 'O-', '1995-09-14', '456.456.456-45', '(48) 94567-8901', 'Av. das Flores, 180', '88080-300', 'Florianópolis', 'SC', 290, 3),
('Amanda Santos', 'amanda.s@email.com', SHA2('senha123', 256), 'doador', 'B+', '1988-12-03', '567.567.567-56', '(48) 95678-9012', 'Travessa dos Pássaros, 110', '88085-400', 'São José', 'SC', 130, 2),
('Felipe Pereira', 'felipe.p@email.com', SHA2('senha123', 256), 'doador', 'A+', '1993-05-19', '678.678.678-67', '(48) 96789-0123', 'Rua Central, 200', '88090-500', 'Palhoça', 'SC', 380, 4),
('Carla Mendes', 'carla.m@email.com', SHA2('senha123', 256), 'doador', 'AB+', '1991-11-25', '789.789.789-78', '(48) 97890-1234', 'Alameda do Sol, 70', '88095-600', 'Florianópolis', 'SC', 95, 1),
('Marcos Rocha', 'marcos.r@email.com', SHA2('senha123', 256), 'doador', 'O+', '1987-04-08', '890.890.890-89', '(48) 98901-2345', 'Praça da Lua, 130', '88100-700', 'São José', 'SC', 240, 3),
('Larissa Alves', 'larissa.a@email.com', SHA2('senha123', 256), 'doador', 'B-', '1994-08-17', '901.901.901-90', '(48) 99012-3456', 'Rua das Pedras, 85', '88105-800', 'Palhoça', 'SC', 170, 2),

-- Hemocentros adicionais (5 registros)
('Hemocentro Joinville', 'hemo.joinville@email.com', SHA2('senha123', 256), 'hemocentro', '(47) 3333-4444', 'Av. Santos Dumont, 1000 - Centro', NULL, NULL, NULL),
('Hemocentro Blumenau', 'hemo.blumenau@email.com', SHA2('senha123', 256), 'hemocentro', '(47) 4444-5555', 'Rua XV de Novembro, 500 - Centro', NULL, NULL, NULL),
('Hemocentro Itajaí', 'hemo.itajai@email.com', SHA2('senha123', 256), 'hemocentro', '(47) 5555-6666', 'Rua Hercílio Luz, 200 - Centro', NULL, NULL, NULL),
('Hemocentro Criciúma', 'hemo.criciuma@email.com', SHA2('senha123', 256), 'hemocentro', '(48) 6666-7777', 'Av. Centenário, 300 - Centro', NULL, NULL, NULL),
('Hemocentro Lages', 'hemo.lages@email.com', SHA2('senha123', 256), 'hemocentro', '(49) 7777-8888', 'Rua Benjamin Constant, 150 - Centro', NULL, NULL, NULL);

-- Inserções adicionais de hemocentros
INSERT INTO hemocentros (nome, endereco, telefone, latitude, longitude, horario_funcionamento, email, cnpj) VALUES
('Hemocentro Joinville', 'Av. Santos Dumont, 1000 - Centro', '(47) 3333-4444', -26.3044, -48.8467, 'Seg-Sab: 7h-19h', 'hemo.joinville@email.com', '12.345.678/0001-01'),
('Hemocentro Blumenau', 'Rua XV de Novembro, 500 - Centro', '(47) 4444-5555', -26.9186, -49.0661, 'Ter-Dom: 8h-20h', 'hemo.blumenau@email.com', '23.456.789/0001-02'),
('Hemocentro Itajaí', 'Rua Hercílio Luz, 200 - Centro', '(47) 5555-6666', -26.9025, -48.6613, 'Qua-Seg: 9h-18h', 'hemo.itajai@email.com', '34.567.890/0001-03'),
('Hemocentro Criciúma', 'Av. Centenário, 300 - Centro', '(48) 6666-7777', -28.6776, -49.3697, 'Seg-Sex: 7h-17h', 'hemo.criciuma@email.com', '45.678.901/0001-04'),
('Hemocentro Lages', 'Rua Benjamin Constant, 150 - Centro', '(49) 7777-8888', -27.8159, -50.3262, 'Seg-Sab: 8h-18h', 'hemo.lages@email.com', '56.789.012/0001-05');

-- Relacionamentos hemocentro_usuario
INSERT INTO hemocentro_usuario (hemocentro_id, usuario_id) VALUES
-- Luiz (mail@email.com) é responsável pelo Hemocentro Florianópolis
(1, 2),

-- Outros relacionamentos
(2, (SELECT id FROM usuarios WHERE email = 'admin.hemopalhoca@email.com')),
(3, (SELECT id FROM usuarios WHERE email = 'hemo.joinville@email.com')),
(4, (SELECT id FROM usuarios WHERE email = 'hemo.blumenau@email.com')),
(5, (SELECT id FROM usuarios WHERE email = 'hemo.itajai@email.com')),
(6, (SELECT id FROM usuarios WHERE email = 'hemo.criciuma@email.com')),
(7, (SELECT id FROM usuarios WHERE email = 'hemo.lages@email.com'));

-- Agendamentos adicionais (50 registros)
INSERT INTO agendamentos (usuario_id, hemocentro_id, data_agendamento, horario, status, observacoes) VALUES
-- Agendamentos para o usuário Luiz (email@email.com)
(1, 1, '2023-09-10', '10:00:00', 'Concluído', 'Primeira doação'),
(1, 1, '2023-11-15', '09:00:00', 'Concluído', 'Segunda doação'),
(1, 1, '2024-01-10', '10:30:00', 'Concluído', 'Terceira doação'),
(1, 2, '2024-03-05', '14:00:00', 'Concluído', 'Doação em hemocentro diferente'),
(1, 1, '2024-05-20', '11:00:00', 'Agendado', 'Próxima doação'),
(1, 3, '2023-10-12', '08:30:00', 'Concluído', NULL),
(1, 1, '2024-02-18', '15:00:00', 'Cancelado', 'Remarcado para março'),

-- Agendamentos para outros usuários (43 registros)
(3, 1, '2023-09-05', '09:30:00', 'Concluído', NULL),
(4, 2, '2023-09-12', '14:00:00', 'Concluído', NULL),
(5, 3, '2023-09-18', '10:00:00', 'Concluído', 'Primeira doação'),
(6, 1, '2023-09-25', '11:30:00', 'Concluído', NULL),
(7, 2, '2023-10-02', '08:00:00', 'Concluído', NULL),
(8, 3, '2023-10-09', '13:00:00', 'Concluído', NULL),
(9, 1, '2023-10-16', '16:00:00', 'Concluído', NULL),
(10, 2, '2023-10-23', '09:30:00', 'Concluído', NULL),
(11, 3, '2023-10-30', '14:30:00', 'Concluído', NULL),
(12, 1, '2023-11-06', '10:00:00', 'Concluído', NULL),
(13, 2, '2023-11-13', '15:00:00', 'Concluído', NULL),
(14, 3, '2023-11-20', '08:30:00', 'Concluído', NULL),
(15, 1, '2023-11-27', '13:30:00', 'Concluído', NULL),
(16, 2, '2023-12-04', '09:00:00', 'Concluído', NULL),
(17, 3, '2023-12-11', '14:00:00', 'Concluído', NULL),
(18, 1, '2023-12-18', '10:30:00', 'Concluído', NULL),
(19, 2, '2023-12-25', '15:30:00', 'Concluído', 'Doação de natal'),
(20, 3, '2024-01-01', '08:00:00', 'Concluído', 'Doação de ano novo'),
(3, 1, '2024-01-08', '13:00:00', 'Concluído', NULL),
(4, 2, '2024-01-15', '09:30:00', 'Concluído', NULL),
(5, 3, '2024-01-22', '14:30:00', 'Concluído', NULL),
(6, 1, '2024-01-29', '10:00:00', 'Concluído', NULL),
(7, 2, '2024-02-05', '15:00:00', 'Concluído', NULL),
(8, 3, '2024-02-12', '08:30:00', 'Concluído', NULL),
(9, 1, '2024-02-19', '13:30:00', 'Concluído', NULL),
(10, 2, '2024-02-26', '09:00:00', 'Concluído', NULL),
(11, 3, '2024-03-04', '14:00:00', 'Concluído', NULL),
(12, 1, '2024-03-11', '10:30:00', 'Concluído', NULL),
(13, 2, '2024-03-18', '15:30:00', 'Concluído', NULL),
(14, 3, '2024-03-25', '08:00:00', 'Concluído', NULL),
(15, 1, '2024-04-01', '13:00:00', 'Concluído', NULL),
(16, 2, '2024-04-08', '09:30:00', 'Concluído', NULL),
(17, 3, '2024-04-15', '14:30:00', 'Concluído', NULL),
(18, 1, '2024-04-22', '10:00:00', 'Concluído', NULL),
(19, 2, '2024-04-29', '15:00:00', 'Concluído', NULL),
(20, 3, '2024-05-06', '08:30:00', 'Agendado', NULL),
(3, 1, '2024-05-13', '13:30:00', 'Agendado', NULL),
(4, 2, '2024-05-20', '09:00:00', 'Agendado', NULL),
(5, 3, '2024-05-27', '14:00:00', 'Agendado', NULL),
(6, 1, '2024-06-03', '10:30:00', 'Agendado', NULL),
(7, 2, '2024-06-10', '15:30:00', 'Agendado', NULL),
(8, 3, '2024-06-17', '08:00:00', 'Agendado', NULL),
(9, 1, '2024-06-24', '13:00:00', 'Agendado', NULL),
(10, 2, '2024-07-01', '09:30:00', 'Agendado', NULL);

-- Campanhas adicionais (15 registros)
INSERT INTO campanhas (hemocentro_id, titulo, mensagem, urgencia, data_inicio, data_fim, ativa) VALUES
(1, 'Dia do Doador Voluntário', 'Celebre conosco o dia do doador voluntário!', 'Média', '2024-03-25', '2024-03-25', TRUE),
(2, 'Férias com Solidariedade', 'Doe sangue nas suas férias e ganhe um brinde!', 'Baixa', '2024-01-01', '2024-02-29', FALSE),
(3, 'Tipo O- Urgente', 'Estoque crítico de sangue O negativo', 'Alta', '2024-04-01', '2024-04-07', TRUE),
(4, 'Maratona de Doação', 'Ajudem-nos a bater o recorde de doações!', 'Média', '2024-05-15', '2024-05-20', TRUE),
(5, 'Doe no Inverno', 'O inverno é quando mais precisamos!', 'Baixa', '2024-06-01', '2024-08-31', TRUE),
(1, 'Dia das Mães Especial', 'Presenteie uma mãe com sua doação', 'Média', '2024-05-05', '2024-05-12', TRUE),
(2, 'Campanha de Verão', 'O verão é quando os estoques mais caem', 'Alta', '2023-12-01', '2024-02-29', FALSE),
(3, 'Doe e Concorra', 'Cada doação dá direito a um cupom', 'Baixa', '2024-04-15', '2024-05-15', TRUE),
(4, 'Aniversário do Hemocentro', '25 anos salvando vidas!', 'Média', '2024-07-01', '2024-07-31', TRUE),
(5, 'Volta às Aulas Solidária', 'Comece o semestre fazendo o bem', 'Baixa', '2024-02-15', '2024-03-15', FALSE),
(1, 'Dia Mundial do Sangue', 'Evento especial no dia 14/06', 'Média', '2024-06-10', '2024-06-16', TRUE),
(2, 'Fim de Ano Solidário', 'Doe sangue e ajude a salvar vidas no fim de ano', 'Alta', '2023-12-15', '2023-12-31', FALSE),
(3, 'Páscoa com Amor', 'Doe sangue nessa páscoa', 'Baixa', '2024-03-25', '2024-04-01', TRUE),
(4, 'Dia dos Pais', 'Seja um herói como seu pai', 'Média', '2024-08-01', '2024-08-11', TRUE),
(5, 'Natal Solidário', 'O melhor presente é salvar vidas', 'Alta', '2024-12-01', '2024-12-25', TRUE);

-- Estoque de sangue adicional
INSERT INTO estoque_sangue (hemocentro_id, tipo_sanguineo, quantidade) VALUES
-- Hemocentro Joinville
(3, 'A+', 18),
(3, 'A-', 6),
(3, 'B+', 12),
(3, 'B-', 4),
(3, 'AB+', 9),
(3, 'AB-', 3),
(3, 'O+', 24),
(3, 'O-', 5),

-- Hemocentro Blumenau
(4, 'A+', 15),
(4, 'A-', 5),
(4, 'B+', 10),
(4, 'B-', 3),
(4, 'AB+', 7),
(4, 'AB-', 2),
(4, 'O+', 20),
(4, 'O-', 4),

-- Hemocentro Itajaí
(5, 'A+', 12),
(5, 'A-', 4),
(5, 'B+', 8),
(5, 'B-', 2),
(5, 'AB+', 6),
(5, 'AB-', 1),
(5, 'O+', 18),
(5, 'O-', 3),

-- Hemocentro Criciúma
(6, 'A+', 10),
(6, 'A-', 3),
(6, 'B+', 7),
(6, 'B-', 2),
(6, 'AB+', 5),
(6, 'AB-', 1),
(6, 'O+', 15),
(6, 'O-', 3),

-- Hemocentro Lages
(7, 'A+', 8),
(7, 'A-', 2),
(7, 'B+', 6),
(7, 'B-', 1),
(7, 'AB+', 4),
(7, 'AB-', 1),
(7, 'O+', 12),
(7, 'O-', 2);

-- Conquistas adicionais para usuários
INSERT INTO usuario_conquistas (usuario_id, conquista_id, data_conquista) VALUES
-- Luiz (email@email.com) tem várias conquistas
(1, 1, '2023-09-10 10:30:00'),
(1, 2, '2024-01-10 11:00:00'),
(1, 4, '2023-12-15 09:00:00'),

-- Outros usuários com conquistas
(3, 1, '2023-09-05 10:00:00'),
(3, 2, '2024-01-08 14:00:00'),
(4, 1, '2023-09-12 15:00:00'),
(5, 1, '2023-09-18 11:00:00'),
(5, 5, '2023-11-20 08:30:00'),
(6, 1, '2023-09-25 12:00:00'),
(7, 1, '2023-10-02 09:00:00'),
(8, 1, '2023-10-09 14:00:00'),
(9, 1, '2023-10-16 17:00:00'),
(10, 1, '2023-10-23 10:00:00'),
(11, 1, '2023-10-30 15:00:00'),
(12, 1, '2023-11-06 11:00:00'),
(13, 1, '2023-11-13 16:00:00'),
(14, 1, '2023-11-20 09:00:00'),
(15, 1, '2023-11-27 14:00:00'),
(16, 1, '2023-12-04 10:00:00'),
(17, 1, '2023-12-11 15:00:00'),
(18, 1, '2023-12-18 11:00:00'),
(19, 1, '2023-12-25 16:00:00'),
(20, 1, '2024-01-01 09:00:00');