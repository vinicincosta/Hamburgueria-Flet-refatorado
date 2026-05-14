"""
helpers.py
----------
Funções auxiliares de lógica de negócio do app Flet.

Responsabilidade: centralizar cálculos e montagens de dados que antes
estavam duplicados ou embutidos em eventos de UI dentro do app.py.

Funções exportadas:
  - calcular_total_carrinho(carrinho)
  - montar_detalhamento(item)
  - calcular_observacoes_e_valor(item, receita_base, preco_ingredientes)
  - montar_ingredientes_iniciais(item, receita_original, ingredientes_disponiveis)
  - recalcular_observacoes(valores_atualizados, receita_original)

Nenhuma dessas funções acessa page, faz chamadas HTTP ou altera estado.
São funções puras que recebem dados e retornam dados.
"""

# ---------------------------------------------------------------------------
# CÁLCULO DE TOTAIS
# ---------------------------------------------------------------------------

def calcular_total_carrinho(carrinho: list) -> float:
    """
    Calcula o valor total de todos os itens do carrinho.

    Regra:
      - Se o item tem lanche: usa valor_lanche * qtd
      - Se o item tem bebida: usa valor_bebida * qtd
      - Items sem nenhum dos dois são ignorados (valor 0)

    Parâmetros:
      carrinho — lista de dicts de itens (formato do client_storage)

    Retorna:
      float — valor total do carrinho
    """
    total = 0.0

    for item in carrinho:
        qtd = int(item.get("qtd", 1))

        if item.get("id_lanche"):
            total += float(item.get("valor_lanche", 0)) * qtd
        elif item.get("id_bebida"):
            total += float(item.get("valor_bebida", 0)) * qtd

    return total


# ---------------------------------------------------------------------------
# MONTAGEM DE STRINGS DE DETALHAMENTO
# ---------------------------------------------------------------------------

def montar_detalhamento(item: dict) -> str:
    """
    Monta a string de detalhamento de um item do carrinho para envio à API.

    Formato:
      "Lanche: <nome> | Bebida: <nome> | Obs: <texto>"

    Parâmetros:
      item — dict do carrinho (pode conter id_lanche, id_bebida, observacoes_texto)

    Retorna:
      str — detalhamento formatado
    """
    nome_lanche = item.get("nome_lanche", "---")
    nome_bebida = item.get("nome_bebida", "---")
    obs_texto   = item.get("observacoes_texto", "Nenhuma")

    return (
        f"Lanche: {nome_lanche} | "
        f"Bebida: {nome_bebida} | "
        f"Obs: {obs_texto}"
    )


# ---------------------------------------------------------------------------
# PROCESSAMENTO DE OBSERVAÇÕES E CÁLCULO DE VALOR (FECHAMENTO DE MESA)
# ---------------------------------------------------------------------------

def calcular_observacoes_e_valor(
    item: dict,
    receita_base: dict,
    preco_ingredientes: dict
) -> tuple:
    """
    Calcula as observações (adicionar/remover) e o valor final de um item
    do carrinho do garçom no momento do fechamento de mesa.

    Essa lógica era duplicada dentro de confirmar_venda_garcom() no app.py.
    Centralizada aqui para que o evento de UI apenas chame esta função.

    Parâmetros:
      item               — dict do carrinho (com ingredientes, valor_lanche, etc.)
      receita_base       — dict {insumo_id: qtd_base} retornado pela API
      preco_ingredientes — dict {insumo_id: custo_unitario}

    Retorna:
      (observacoes, valor_final, detalhamento) onde:
        observacoes  — {"adicionar": [...], "remover": [...]}
        valor_final  — float com o valor ajustado do item
        detalhamento — str descritiva para persistência
    """
    id_lanche  = item.get("id_lanche")
    id_bebida  = item.get("id_bebida")
    qtd_lanche = int(item.get("qtd", 1))

    observacoes  = {"adicionar": [], "remover": []}
    valor_final  = 0.0
    detalhamento = ""

    if id_lanche:
        # Compara ingredientes atuais com a receita base para montar observações
        ingredientes = item.get("ingredientes", {})

        for ing_id, qtd in ingredientes.items():
            qtd_base = receita_base.get(ing_id, 0)

            if qtd > qtd_base:
                observacoes["adicionar"].append({
                    "insumo_id": ing_id,
                    "qtd": qtd - qtd_base,
                    "valor": preco_ingredientes.get(ing_id, 0) * (qtd - qtd_base)
                })
            elif qtd < qtd_base:
                observacoes["remover"].append({
                    "insumo_id": ing_id,
                    "qtd": qtd_base - qtd
                })

        # Valor base + extras dos adicionais
        valor_base  = float(item.get("valor_original_lanche", item.get("valor_lanche", 0)))
        valor_extra = sum(obs.get("valor", 0) for obs in observacoes["adicionar"])
        valor_final = (valor_base + valor_extra) * qtd_lanche

        detalhamento = (
            f"Lanche: {item.get('nome_lanche', 'Sem nome')} | "
            f"Obs: {item.get('observacoes_texto', 'Nenhuma')}"
        )

    elif id_bebida:
        valor_final  = float(item.get("valor", 0)) * qtd_lanche
        detalhamento = f"Bebida: {item.get('nome_bebida', 'Sem nome')}"

    return observacoes, valor_final, detalhamento


# ---------------------------------------------------------------------------
# MONTAGEM DE INGREDIENTES INICIAIS (TELA DE OBSERVAÇÕES)
# ---------------------------------------------------------------------------

def montar_ingredientes_iniciais(
    item: dict,
    receita_original: dict,
    ingredientes_disponiveis: dict
) -> dict:
    """
    Determina o estado inicial dos ingredientes ao abrir a tela de observações.

    Regra:
      - Se o item já foi editado antes: usa os ingredientes salvos (respeitando edições)
      - Se é a primeira vez: usa a receita original do lanche
      - Garante que todos os ingredientes disponíveis apareçam (novos começam com 0)

    Essa lógica era duplicada nas duas telas de observações (/observacoes e
    /observacoes_garcom), com pequenas diferenças de implementação.
    Centralizada aqui com comportamento unificado.

    Parâmetros:
      item                    — dict do item do carrinho
      receita_original        — dict {insumo_id: qtd_base} da receita base do lanche
      ingredientes_disponiveis — dict {insumo_id: nome_insumo} dos insumos disponíveis

    Retorna:
      dict {insumo_id: quantidade_atual} — estado inicial dos controles visuais
    """
    ingredientes_salvos_raw = item.get("ingredientes")

    if ingredientes_salvos_raw:
        # Edição subsequente: respeita o que já foi salvo (pode ter chaves int ou str)
        ingredientes_iniciais = {int(k): v for k, v in ingredientes_salvos_raw.items()}
    else:
        # Primeira abertura: parte da receita original
        ingredientes_iniciais = dict(receita_original)

    # Garante que TODOS os ingredientes disponíveis apareçam nos controles.
    # Ingredientes fora da receita original começam com 0 (podem ser adicionados).
    for ing_id in ingredientes_disponiveis:
        if ing_id not in ingredientes_iniciais:
            ingredientes_iniciais[ing_id] = 0

    return ingredientes_iniciais


# ---------------------------------------------------------------------------
# RECÁLCULO DE OBSERVAÇÕES (AO SALVAR NA TELA DE OBSERVAÇÕES)
# ---------------------------------------------------------------------------

def recalcular_observacoes(
    valores_atualizados: dict,
    receita_original: dict
) -> dict:
    """
    Recalcula o dict de observações comparando os valores atuais dos controles
    com a receita original do lanche.

    Regra:
      - qtd_nova > qtd_base  → adicionar (qtd_nova - qtd_base)
      - qtd_nova < qtd_base  → remover   (qtd_base - qtd_nova)
      - qtd_nova == qtd_base → sem alteração
      - ing_id fora da receita e qtd_nova > 0 → adicionar como ingrediente extra

    Essa lógica era duplicada em salvar_observacoes() nas duas telas de
    observações (/observacoes e /observacoes_garcom).

    Parâmetros:
      valores_atualizados — dict {insumo_id: qtd_atual} dos controles visuais
      receita_original    — dict {insumo_id: qtd_base} da receita base

    Retorna:
      dict {"adicionar": [...], "remover": [...]}
    """
    observacoes = {"adicionar": [], "remover": []}

    # Processa ingredientes que já existem na receita base
    for ing_id, qtd_base in receita_original.items():
        qtd_nova = valores_atualizados.get(ing_id, 0)

        if qtd_nova > qtd_base:
            observacoes["adicionar"].append({
                "insumo_id": ing_id,
                "qtd": qtd_nova - qtd_base
            })
        elif qtd_nova < qtd_base:
            observacoes["remover"].append({
                "insumo_id": ing_id,
                "qtd": qtd_base - qtd_nova
            })

    # Processa ingredientes extras (fora da receita base, adicionados manualmente)
    for ing_id, qtd_nova in valores_atualizados.items():
        if ing_id not in receita_original and qtd_nova > 0:
            observacoes["adicionar"].append({
                "insumo_id": ing_id,
                "qtd": qtd_nova
            })

    return observacoes
