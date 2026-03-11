# Casos de Teste - Semantic Search

**Projeto:** fullcycle-semantic-search
**Tipo:** Testes manuais via API e Chat
**Ultima execucao:** 2026-03-11
**Documento:** Lista de empresas ficticias com nome, setor, faturamento (R$) e ano de fundacao

---

## 1. Perguntas Diretas

Perguntas objetivas com resposta direta no documento.

| # | Pergunta | Resposta Esperada | Status |
|---|----------|-------------------|--------|
| 1 | Liste todas as empresas mencionadas no documento | Lista extensa de empresas (Alta, Atlas, Matriz, Mirage, Zenith, Agil, Aurora, Azul, Beta, Grao, Horizonte, etc.) | PASSED |
| 2 | Quais setores de atuacao aparecem no documento? | Comercio, Holding, Siderurgia, Tecnologia, Varejo, Agronegocio, Servicos, Bebidas, Biotech, Energia, Logistica, Mineracao, Petroleo, Turismo, IA, Saude, entre outros | PASSED |
| 3 | Qual empresa tem o maior faturamento? | Helix Software LTDA com R$ 4.511.842.713,72 ou Alianca Esportes ME com R$ 4.485.320.049,16 (ambas acima de 4 bilhoes) | PASSED |
| 4 | Qual a empresa mais antiga e qual a mais recente? | Mais antiga: fundada entre 1930-1937. Mais recente: Delta Higiene S.A., fundada em 2024 | PASSED |
| 5 | Existem empresas do tipo LTDA no setor de cosmeticos? | Sim, Mirage Cosmeticos LTDA | PASSED |
| 6 | Quais indicadores financeiros sao apresentados para as empresas? | Faturamento em Reais (R$) e ano de fundacao | PASSED |
| 7 | Faca um resumo geral do documento | Lista de empresas ficticias com nome, setor, tipo societario, faturamento e ano de fundacao | PASSED |

---

## 2. Perguntas Analiticas

Perguntas que exigem cruzamento de dados, comparacao ou inferencia.

| # | Pergunta | Resposta Esperada | Status |
|---|----------|-------------------|--------|
| 8 | Quantas empresas do setor de tecnologia existem no documento? | Aproximadamente 10 empresas (Magna Tecnologia, Matriz Software, Orbital Tecnologia, Alta Tecnologia, Onix Tecnologia, etc.) | PASSED |
| 9 | Compare as empresas do setor de energia com as do setor de petroleo em termos de faturamento | Deve listar empresas de ambos os setores com seus faturamentos e fazer comparacao (petroleo tende a ter faturamentos maiores) | PASSED |
| 10 | Quais empresas tem faturamento acima de 1 bilhao de reais? | Helix Software LTDA, Alianca Esportes ME, Gamma IA LTDA, Lunar Biotech Comercio, Lunar Higiene Comercio, Lunar Logistica S.A., Azul Petroleo Comercio, entre outras | PASSED |
| 11 | Quais empresas foram fundadas antes de 1950? | Lista extensa incluindo Alta Construtora Participacoes (1931), Aurora Educacao Industria (1932), Atlas Petroleo Servicos (1934), Zenith Automotiva Servicos (1935), etc. | PASSED |
| 12 | Qual setor possui mais empresas listadas? | Deve identificar setores com maior concentracao de empresas (Comercio, Servicos e Industria entre os maiores) | PASSED |
| 13 | Qual o faturamento medio das empresas do setor de varejo? | Deve calcular ou estimar a media com base nas empresas de varejo listadas | PASSED |

---

## 3. Perguntas de Analise de Dados

Perguntas que exigem agregacao, contagem ou calculo sobre os dados.

| # | Pergunta | Resposta Esperada | Status |
|---|----------|-------------------|--------|
| 14 | Quantas empresas sao do tipo S.A. versus LTDA? | Deve contar e comparar a quantidade de empresas S.A. e LTDA no documento | PASSED |
| 15 | Agrupe as empresas por decada de fundacao e diga quantas foram fundadas em cada decada | Deve agrupar empresas por decada (1930s, 1940s, ..., 2020s) com contagem por decada | PASSED |
| 16 | Quais sao as 5 empresas com menor faturamento? | Deve identificar empresas com faturamentos menores (valores abaixo de R$ 1 milhao) | PASSED |
| 17 | Existem empresas do grupo Lunar? Quais sao e em quais setores atuam? | Sim: Lunar Biotech Comercio, Lunar Higiene Comercio, Lunar Logistica S.A., Lunar Mineracao Participacoes, Lunar Automotiva ME, Lunar Bebidas LTDA, etc. | PASSED |
| 18 | Quais empresas do setor de agronegocio foram fundadas apos 2000? | Deve filtrar empresas de agronegocio com ano de fundacao > 2000 | PASSED |

---

## 4. Perguntas Fora do Escopo (Guardrail)

Perguntas que NAO tem resposta no documento. O sistema deve recusar responder.

| # | Pergunta | Resposta Esperada | Status |
|---|----------|-------------------|--------|
| 19 | Qual a receita de bolo de chocolate? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 20 | Quem eh o presidente do Brasil? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 21 | Explique a teoria da relatividade de Einstein | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 22 | Qual o PIB do Brasil em 2024? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 23 | Me fale sobre a empresa Tesla | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 24 | Qual a cotacao do dolar hoje? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 25 | Como programar em Python? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 26 | Quem ganhou a Copa do Mundo de 2022? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 27 | Qual a capital da Australia? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |
| 28 | O que eh inteligencia artificial? | "Nao tenho informacoes necessarias para responder sua pergunta." | PASSED |

---

## 5. Perguntas de Borda (Edge Cases)

Perguntas ambiguas ou que misturam contexto do documento com temas externos.

| # | Pergunta | Resposta Esperada | Status |
|---|----------|-------------------|--------|
| 29 | Quais sao as empresas que comecam com o nome Azul? Liste todas com seus setores e faturamento | Deve listar todas as empresas Azul (Automotiva, Biotech, Dados, Energia, Entretenimento, Eventos, Hardware, Higiene, IA, Petroleo, Sustentavel, Turismo) com faturamentos | PASSED |
| 30 | Quais empresas de IA existem e como elas se comparam com o ChatGPT? | Deve listar empresas de IA do documento (Gamma IA, Pacto IA, Azul IA, Beta IA, Horizonte IA, Alfa IA) sem comparar com ChatGPT | PASSED |
| 31 | O documento menciona alguma empresa de criptomoedas ou blockchain? | Deve responder que nao ha empresas desses setores no documento | PASSED |

---

## Como Executar os Testes

### Via API (curl)

```bash
# Pergunta direta
curl -s -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "SUA PERGUNTA AQUI", "k": 20}'

# Com formatacao
curl -s -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "SUA PERGUNTA AQUI", "k": 20}' | python3 -m json.tool
```

### Via CLI Direto (sem servidor)

```bash
make chat
# Digitar a pergunta no prompt QUESTION:
```

### Via CLI HTTP (com servidor rodando)

```bash
make chat-api
# Digitar a pergunta no prompt QUESTION:
```

---

## Criterios de Aprovacao

| Criterio | Descricao |
|----------|-----------|
| Resposta correta | A resposta contem informacoes reais e verificaveis do documento |
| Sem alucinacao | A resposta NAO contem dados inventados ou de fontes externas |
| Guardrail ativo | Perguntas fora do escopo recebem "Nao tenho informacoes necessarias..." |
| Tempo de resposta | Resposta retornada em menos de 30 segundos |
| Formato consistente | Resposta em texto corrido, sem erros de encoding |

---

## Resumo

| Categoria | Total | Passou | Falhou |
|-----------|-------|--------|--------|
| Perguntas Diretas | 7 | 7 | 0 |
| Perguntas Analiticas | 6 | 6 | 0 |
| Analise de Dados | 5 | 5 | 0 |
| Guardrail (fora do escopo) | 10 | 10 | 0 |
| Edge Cases | 3 | 3 | 0 |
| **Total** | **31** | **31** | **0** |
