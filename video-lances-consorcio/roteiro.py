"""Roteiro do vídeo (compartilhado pela voz sintética e pela voz gravada)."""
# cena -> [(id, texto falado, legenda)]
ROTEIRO = [
 ('intro', [
  ('i1', 'A todo momento, tem gente querendo ser contemplado no consórcio.',
         'A todo momento, tem gente querendo ser contemplado no consórcio.'),
  ('i2', 'Mas existem quatro pistas pra chegar lá. E em uma delas, a concorrência é bem menor.',
         'Mas existem 4 pistas pra chegar lá. E em uma delas, a concorrência é bem menor.')]),
 ('sorteio', [
  ('s1', 'Pista um: o sorteio.', 'Pista 1: o sorteio.'),
  ('s2', 'Aqui, você não paga nada a mais.', 'Aqui, você não paga nada a mais.'),
  ('s3', 'Todo mundo com a parcela em dia concorre, com a mesma chance.',
         'Todo mundo com a parcela em dia concorre, com a mesma chance.'),
  ('s4', 'É pura sorte.', 'É pura sorte.')]),
 ('livre', [
  ('l1', 'Pista dois: o lance livre.', 'Pista 2: o lance livre.'),
  ('l2', 'Funciona como um leilão.', 'Funciona como um leilão.'),
  ('l3', 'Você oferta o percentual da carta que quiser, e leva quem der o maior lance.',
         'Você oferta o percentual da carta que quiser, e leva quem der o maior lance.'),
  ('l4', 'Por isso, costuma ser a pista mais disputada.', 'Por isso, costuma ser a pista mais disputada.')]),
 ('fixo', [
  ('f1', 'Pista três: o lance fixo.', 'Pista 3: o lance fixo.'),
  ('f2', 'O percentual já vem definido pela administradora.', 'O percentual já vem definido pela administradora.'),
  ('f3', 'Por exemplo, trinta por cento.', 'Por exemplo, 30%.'),
  ('f4', 'Todo mundo oferta o mesmo valor, e o desempate é por sorteio.',
         'Todo mundo oferta o mesmo valor, e o desempate é por sorteio.')]),
 ('fidelidade', [
  ('d1', 'Pista quatro: o lance fidelidade.', 'Pista 4: o lance fidelidade.'),
  ('d2', 'É uma pista reservada pra quem já está há mais tempo no grupo, com as parcelas em dia.',
         'É uma pista reservada pra quem já está há mais tempo no grupo, com as parcelas em dia.'),
  ('d3', 'Como pouca gente pode entrar, a concorrência é bem menor.',
         'Como pouca gente pode entrar, a concorrência é bem menor.')]),
 ('recap', [
  ('r1', 'E qual é a melhor pista?', 'E qual é a melhor pista?'),
  ('r2', 'Depende do seu caixa, do seu prazo, e das regras do seu grupo.',
         'Depende do seu caixa, do seu prazo e das regras do seu grupo.')]),
 ('cta', [
  ('c1', 'Comenta lance, que eu te ajudo a montar a sua estratégia.',
         'Comenta LANCE que eu te ajudo a montar a sua estratégia.')]),
]
# contemplação (cruzar a linha) em cada pista: (frase de referência, 's'|'e', deslocamento)
WIN = {'sorteio': ('s4', 'e', 0.5), 'livre': ('l3', 'e', 0.35), 'fixo': ('f4', 'e', 0.7), 'fidelidade': ('d3', 'e', 0.35)}
LEAD, GAP, TAIL = 0.45, 0.24, 0.55

