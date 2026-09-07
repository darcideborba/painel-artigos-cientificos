# Prompt / instrução usada para gerar este painel

Este painel não nasceu de um pipeline totalmente automatizado: ele é produzido em uma sessão de trabalho com o Claude (Anthropic, modo Cowork), que faz a busca, a curadoria e a montagem do HTML a partir da instrução abaixo. O script `gerar_painel.py` neste repositório automatiza a parte que pode ser automatizada (busca e template); a curadoria fina (relevância, resumo, ranking) é feita pela IA seguindo estes critérios.

## Instrução (prompt) usada

> Monte um "Painel Diário de Artigos Científicos" em uma página HTML autocontida (sem dependências externas), com visual escuro, organizada por temas.
>
> Temas de interesse: transformação digital, governo digital, administração pública, governança, capacidades dinâmicas, processos, inteligência artificial, ciência de dados, comportamento organizacional, gestão e políticas públicas.
>
> Para cada tema, busque de 3 a 6 artigos científicos recentes (prioritariamente dos últimos 12 meses) em bases acadêmicas confiáveis (Consensus, Scite, e como alternativa Semantic Scholar), com preferência por artigos genuinamente aplicáveis e por regulação/governo, evitando trabalhos excessivamente específicos ou de nicho.
>
> Para cada artigo, extraia: título, autores/ano, periódico, um resumo curto (2 a 3 linhas, em português) do achado principal, e o link direto (DOI ou página do periódico).
>
> Organize os artigos em cards dentro de seções por tema, com contagem de itens por seção, uma etiqueta "novo" para publicações do último mês, e um cabeçalho com a data de geração do painel.
>
> Não reproduza o texto integral de nenhum artigo; apenas resuma e linke a fonte original.

## Critérios de curadoria (regras gerais do usuário)

- Escolher apenas artigos genuinamente aplicáveis ao tema, com preferência por regulação governamental.
- Evitar artigos excessivamente específicos ou de nicho estreito.
- Usar fontes acadêmicas confiáveis.
- Painel gerado sob demanda (não mais em cadência automática desde 19/08/2026); atualizar apenas quando solicitado.

## Fontes de dados originalmente usadas

Consensus e Scite (via MCP), ambas com cotas mensais limitadas. O script incluído aqui usa a API pública do Semantic Scholar como alternativa reprodutível sem necessidade de chave paga.
