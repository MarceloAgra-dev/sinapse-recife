-- =====================================================================
-- Sinapse Recife - Dados de exemplo (INSERTs)
-- Todos os pesquisadores de exemplo usam a senha: senha123
-- =====================================================================
PRAGMA foreign_keys = ON;

INSERT INTO instituicoes (nome, sigla) VALUES
 ('Universidade Federal de Pernambuco', 'UFPE'),
 ('Universidade de Pernambuco', 'UPE'),
 ('Instituto Federal de Pernambuco', 'IFPE'),
 ('CESAR School', 'CESAR School');

INSERT INTO areas (nome) VALUES
 ('Engenharia'), ('Saúde'), ('Meio ambiente'), ('Tecnologia'), ('Educação'), ('Mobilidade');

INSERT INTO ods (numero, nome) VALUES
 (3,  'Saúde e bem-estar'),
 (4,  'Educação de qualidade'),
 (8,  'Trabalho decente e crescimento econômico'),
 (9,  'Indústria, inovação e infraestrutura'),
 (11, 'Cidades e comunidades sustentáveis'),
 (13, 'Ação contra a mudança global do clima'),
 (17, 'Parcerias e meios de implementação');

INSERT INTO pesquisadores (nome, email, senha_hash, departamento, instituicao_id) VALUES
 ('Dra. Exemplo Silva',  'silva@exemplo.br',  'pbkdf2:sha256:1000000$E6nYvqEwrE82bVvs$73047355347305c039d0e485110709452649b31397283f2c685ddaa81c0dadcd', 'Engenharia Civil',        1),
 ('Dr. Exemplo Santos',  'santos@exemplo.br', 'pbkdf2:sha256:1000000$E6nYvqEwrE82bVvs$73047355347305c039d0e485110709452649b31397283f2c685ddaa81c0dadcd', 'Mobilidade e Dados',      4),
 ('Dra. Exemplo Lima',   'lima@exemplo.br',   'pbkdf2:sha256:1000000$E6nYvqEwrE82bVvs$73047355347305c039d0e485110709452649b31397283f2c685ddaa81c0dadcd', 'Ciências do Transporte',  2),
 ('Dr. Exemplo Costa',   'costa@exemplo.br',  'pbkdf2:sha256:1000000$E6nYvqEwrE82bVvs$73047355347305c039d0e485110709452649b31397283f2c685ddaa81c0dadcd', 'Gestão Ambiental',        3);

INSERT INTO projetos (titulo, resumo, objetivos, aplicacoes, tipo, maturidade, nivel_detalhe, status, area_id, pesquisador_id) VALUES
 ('Sensores de baixo custo para monitorar alagamentos',
  'Pequenos sensores instalados em canais e ruas medem o nível da água e enviam alertas em tempo real. Assim, a prefeitura pode agir antes que o alagamento aconteça.',
  'Reduzir o tempo de resposta a alagamentos e criar um mapa de risco atualizado da cidade.',
  'Defesa Civil, planejamento urbano, empresas de drenagem e seguradoras.',
  'Protótipo', 'Piloto', 'completo', 'publicado', 1, 1),
 ('Rotas de ônibus mais eficientes com dados abertos',
  'Estudo que usa dados de viagens para sugerir ajustes de rota e reduzir o tempo de espera dos passageiros.',
  'Identificar trechos com maior atraso e propor rotas alternativas.',
  'Secretarias de mobilidade e empresas de transporte público.',
  'Tese', 'Concluído', 'resumo_objetivos', 'publicado', 6, 2),
 ('Bicicletas compartilhadas e acesso ao transporte',
  'Análise de como ciclovias e bicicletas compartilhadas ajudam quem mora longe dos terminais.',
  'Medir o impacto das bicicletas no acesso ao transporte coletivo.',
  'Planejamento urbano e operadoras de bicicletas compartilhadas.',
  'Tese', 'Concluído', 'resumo', 'publicado', 6, 3),
 ('Telemedicina para postos de saúde de bairros periféricos',
  'Atendimento por vídeo com especialistas para reduzir filas e deslocamentos de pacientes.',
  'Levar especialistas a postos de saúde sem precisar mover o paciente.',
  'Secretarias de saúde, hospitais e clínicas.',
  'Projeto', 'Piloto', 'completo', 'publicado', 2, 1),
 ('Compostagem urbana em feiras livres',
  'Sistema simples para transformar resíduos de feiras em adubo para hortas comunitárias.',
  'Reduzir o lixo orgânico das feiras e produzir adubo para a comunidade.',
  'Prefeituras, cooperativas e hortas comunitárias.',
  'Protótipo', 'Protótipo', 'resumo_objetivos', 'publicado', 3, 4),
 ('Plataforma de apoio a microempreendedores',
  'Ferramenta digital que ajuda pequenos negócios a organizar vendas e acessar crédito.',
  'Facilitar a gestão financeira de microempreendedores.',
  'Bancos de fomento, incubadoras e associações comerciais.',
  'Protótipo', 'Protótipo', 'completo', 'publicado', 4, 2),
 ('Monitoramento de qualidade do ar em escolas',
  'Medidores de baixo custo acompanham a qualidade do ar dentro de salas de aula.',
  'Avaliar a qualidade do ar e propor melhorias de ventilação.',
  'Escolas, secretarias de educação e saúde.',
  'Projeto', 'Ideia', 'resumo', 'rascunho', 3, 1);

INSERT INTO projeto_ods (projeto_id, ods_id)
 SELECT p.id, o.id FROM (
   SELECT 1 pid, 9 n UNION ALL SELECT 1, 11 UNION ALL SELECT 1, 13
   UNION ALL SELECT 2, 11 UNION ALL SELECT 2, 9
   UNION ALL SELECT 3, 11
   UNION ALL SELECT 4, 3 UNION ALL SELECT 4, 17
   UNION ALL SELECT 5, 11 UNION ALL SELECT 5, 13
   UNION ALL SELECT 6, 8 UNION ALL SELECT 6, 9
   UNION ALL SELECT 7, 3 UNION ALL SELECT 7, 4
 ) x JOIN projetos p ON p.id = x.pid JOIN ods o ON o.numero = x.n;

INSERT INTO contatos (projeto_id, nome, email, organizacao, interesse, mensagem) VALUES
 (1, 'Carlos Exemplo', 'carlos@empresaexemplo.com', 'Empresa Exemplo Drenagem', 'Projeto-piloto', 'Gostaríamos de testar os sensores em um projeto-piloto.'),
 (1, 'Ana Exemplo', 'ana@obras.exemplo.gov.br', 'Secretaria Exemplo de Obras', 'Informações', 'Podemos receber mais detalhes sobre o mapa de risco?'),
 (2, 'Bruno Exemplo', 'bruno@transporte.exemplo.com', 'Consórcio Exemplo de Transporte', 'Parceria', 'Temos interesse em aplicar o estudo em nossas linhas.');
