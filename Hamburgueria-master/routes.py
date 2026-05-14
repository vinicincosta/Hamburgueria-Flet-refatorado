"""
routes.py
---------
Camada de acesso à API da Hamburgueria.

Responsabilidade única: comunicação HTTP com a API Flask.
  - Sem lógica de negócio
  - Sem manipulação de estado da UI
  - Sem cálculos de receita ou observações (esses ficam em helpers.py)

Todas as funções retornam dados brutos da API ou valores padrão
seguros em caso de erro ([], {}, None), nunca lançam exceções
para cima.
"""

import json
from datetime import datetime

import requests

# URL base da API — altere aqui para apontar para outro ambiente
BASE_URL = "http://10.20.21.170:5000"

# Mapa de status numérico → texto legível para pedidos
_STATUS_PEDIDO = {
    0: "Aprovado",
    1: "Sendo preparado",
    2: "Saindo para Entrega"
}


# ---------------------------------------------------------------------------
# AUTENTICAÇÃO
# ---------------------------------------------------------------------------

def post_login(email: str, senha: str):
    """
    Realiza login na API.

    Retorna:
      (token, papel, nome, None)   — em caso de sucesso
      (None, None, None, mensagem) — em caso de erro
    """
    if not email or not senha:
        return None, None, None, "Email e senha são obrigatórios"

    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": email, "senha": senha},
            timeout=10
        )

        if response.status_code == 200:
            dados = response.json()
            nome = dados.get("nome") or "Nome não disponível"
            return dados.get("access_token"), dados.get("papel"), nome, None

        if response.status_code == 401:
            return None, None, None, "Email ou senha incorretos"
        if response.status_code == 400:
            return None, None, None, "Credenciais inválidas"

        return None, None, None, f"Erro no servidor: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return None, None, None, f"Erro de conexão: {str(e)}"
    except Exception as e:
        return None, None, None, f"Erro inesperado: {str(e)}"


# ---------------------------------------------------------------------------
# PESSOAS
# ---------------------------------------------------------------------------

def post_pessoas(nome_pessoa, cpf, papel, senha, salario, email, status_pessoa):
    """
    Cadastra uma nova pessoa (cliente ou garçom) na API.

    Retorna:
      (dict_pessoa, None)   — sucesso
      (None, mensagem_erro) — falha
    """
    payload = {
        "nome_pessoa":   nome_pessoa,
        "cpf":           cpf,
        "papel":         papel,
        "senha":         senha,
        "salario":       salario,
        "status_pessoa": status_pessoa,
        "email":         email,
    }

    try:
        response = requests.post(f"{BASE_URL}/cadastro_pessoas_login", json=payload)

        if response.status_code == 201:
            return response.json(), None

        return None, response.json().get("msg", "Erro desconhecido")

    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão: {str(e)}"


def listar_pessoas():
    """
    Retorna a lista de todas as pessoas cadastradas.
    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(f"{BASE_URL}/pessoas")

        if response.status_code == 200:
            return response.json().get("pessoas", [])

        print(f"Erro ao listar pessoas: {response.status_code}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao listar pessoas: {e}")
        return []


# ---------------------------------------------------------------------------
# LANCHES
# ---------------------------------------------------------------------------

def cadastrar_lanche_post(novo_lanche: dict):
    """
    Cadastra um novo lanche na API.
    Apenas imprime o resultado — função auxiliar de administração.
    """
    response = requests.post(f"{BASE_URL}/lanches", json=novo_lanche)

    if response.status_code == 201:
        dados = response.json()
        print(
            f"Nome Lanche: {dados['nome_lanche']}\n"
            f"Valor: {dados['valor']}\n"
            f"Descrição: {dados['descricao']}\n"
        )
    else:
        print(f"Erro ao cadastrar lanche: {response.status_code}")


def listar_lanche(token: str) -> list:
    """
    Retorna a lista de lanches disponíveis.
    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/lanches",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            return response.json().get("lanches", [])

        print(f"Erro ao listar lanches: {response.status_code}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao listar lanches: {e}")
        return []


# ---------------------------------------------------------------------------
# BEBIDAS
# ---------------------------------------------------------------------------

def listar_bebidas(token: str) -> list:
    """
    Retorna a lista de bebidas disponíveis.
    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/bebidas",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            return response.json().get("bebidas", [])

        print(f"Erro ao listar bebidas: {response.status_code}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao listar bebidas: {e}")
        return []


# ---------------------------------------------------------------------------
# PEDIDOS
# ---------------------------------------------------------------------------

def listar_pedidos(token: str) -> list:
    """
    Retorna a lista de pedidos ativos, com o campo status_texto resolvido.

    O status numérico (0, 1, 2) é convertido para texto legível via
    _STATUS_PEDIDO para facilitar exibição na UI sem lógica no app.py.

    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/pedidos",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            pedidos = response.json().get("pedidos", [])

            # Resolve status_texto aqui para manter UI livre de mapeamentos
            for p in pedidos:
                p["status_texto"] = _STATUS_PEDIDO.get(p.get("status"), "Desconhecido")

            return pedidos

        print(f"Erro ao listar pedidos: {response.status_code}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao listar pedidos: {e}")
        return []


def cadastrar_pedido_app(
    id_lanche,
    id_bebida,
    qtd_lanche,
    detalhamento,
    numero_mesa,
    observacoes,
    id_pessoa,
    id_venda=None
) -> dict:
    """
    Envia um novo pedido para a API (POST /pedidos).

    Trata automaticamente:
      - numero_mesa "delivery" → string mantida como "delivery"
      - numero_mesa numérico  → convertido para int
      - observacoes None      → {"adicionar": [], "remover": []}
      - id_lanche / id_bebida inválidos → ignorados do payload

    Retorna o dict da resposta da API, ou {"error": mensagem} em falha.
    """
    # Normaliza numero_mesa
    if isinstance(numero_mesa, str) and numero_mesa.strip().lower() == "delivery":
        numero_mesa_val = "delivery"
    else:
        try:
            numero_mesa_val = int(numero_mesa)
        except (ValueError, TypeError):
            print(f"numero_mesa inválido: {numero_mesa}, usando 0")
            numero_mesa_val = 0

    payload = {
        "data_pedido":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "numero_mesa":  numero_mesa_val,
        "id_pessoa":    int(id_pessoa),
        "qtd_lanche":   int(qtd_lanche),
        "detalhamento": detalhamento or "",
        "observacoes":  observacoes or {"adicionar": [], "remover": []},
        "id_venda":     int(id_venda) if id_venda is not None else None,
    }

    # Inclui lanche e bebida apenas se válidos
    if id_lanche not in [None, "", 0, "0"]:
        try:
            payload["id_lanche"] = int(id_lanche)
        except Exception:
            print(f"id_lanche inválido ignorado: {id_lanche}")

    if id_bebida not in [None, "", 0, "0"]:
        try:
            payload["id_bebida"] = int(id_bebida)
        except Exception:
            print(f"id_bebida inválido ignorado: {id_bebida}")

    if "id_lanche" not in payload and "id_bebida" not in payload:
        return {"error": "É necessário informar pelo menos um lanche ou uma bebida"}

    try:
        response = requests.post(f"{BASE_URL}/pedidos", json=payload)

        if response.status_code != 201:
            print(f"Erro cadastrar_pedido_app: {response.status_code} {response.text}")
            return {"error": response.text}

        return response.json()

    except Exception as e:
        print(f"ERRO cadastrar_pedido_app: {e}")
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# VENDAS
# ---------------------------------------------------------------------------

def cadastrar_venda_app(
    pessoa_id,
    detalhamento,
    endereco,
    tipo_venda,
    forma_pagamento,
    valor_venda=0.0,
    lanche_id=None,
    bebida_id=None,
    qtd_lanche=1,
    observacoes=None
) -> dict:
    """
    Registra uma venda na API (POST /vendas).

    Usado em dois contextos:
      1. Delivery: cria a Venda ANTES dos Pedidos para obter o id_venda.
      2. Fechamento de mesa: cria a Venda ao finalizar o atendimento.

    Retorna o dict da resposta da API, ou {"error": mensagem} em falha.
    """
    payload = {
        "data_venda":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lanche_id":       lanche_id,
        "pessoa_id":       pessoa_id,
        "bebida_id":       bebida_id,
        "tipo_venda":      tipo_venda,
        "qtd_lanche":      qtd_lanche,
        "detalhamento":    detalhamento,
        "endereco":        endereco,
        "forma_pagamento": forma_pagamento,
        "observacoes":     observacoes or {"adicionar": [], "remover": []},
        "valor_venda":     valor_venda,
    }

    try:
        response = requests.post(f"{BASE_URL}/vendas", json=payload)

        if response.status_code != 201:
            print(f"Erro cadastrar_venda_app: {response.status_code} {response.text}")
            return {"error": response.text}

        return response.json()

    except Exception as e:
        print(f"ERRO cadastrar_venda_app: {e}")
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# INSUMOS
# ---------------------------------------------------------------------------

def listar_insumos(token: str) -> list:
    """
    Retorna a lista de insumos disponíveis.
    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/insumos",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()

        if "insumos" in data:
            return data["insumos"]

        print(f"Erro ao listar insumos: {data}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao listar insumos: {e}")
        return []


def get_insumo(id_insumo: int) -> dict:
    """Retorna dados de um insumo específico pelo ID."""
    try:
        response = requests.get(f"{BASE_URL}/get_insumo_id/{id_insumo}")

        if response.status_code == 200:
            return response.json()

        print(f"Erro ao buscar insumo {id_insumo}: {response.status_code}")
        return {}

    except Exception as e:
        print(f"Erro de conexão ao buscar insumo: {e}")
        return {}


def update_insumo(id_insumo: int) -> dict:
    """Atualiza estoque calculado de um insumo na API."""
    try:
        response = requests.put(f"{BASE_URL}/update_insumo/{id_insumo}")

        if response.status_code == 200:
            return response.json()

        print(f"Erro ao atualizar insumo {id_insumo}: {response.status_code}")
        return {}

    except Exception as e:
        print(f"Erro ao atualizar insumo: {e}")
        return {}


def update_bebida(id_bebida: int) -> dict:
    """Atualiza estoque calculado de uma bebida na API."""
    try:
        response = requests.put(f"{BASE_URL}/update_bebida/{id_bebida}")

        if response.status_code == 200:
            return response.json()

        print(f"Erro ao atualizar bebida {id_bebida}: {response.status_code}")
        return {}

    except Exception as e:
        print(f"Erro ao atualizar bebida: {e}")
        return {}


# ---------------------------------------------------------------------------
# RECEITA BASE DO LANCHE
# ---------------------------------------------------------------------------

def listar_receita_lanche(lanche_id: int) -> dict:
    """
    Busca a receita base de um lanche na API.

    Retorna:
      dict {insumo_id (int): quantidade_base_em_unidades (int)}

    A API retorna quantidade em gramas (ex: 200), dividimos por 100
    para obter unidades de ajuste compatíveis com os controles de UI
    (cada unidade de ajuste = 100g).

    Retorna {} em caso de erro.
    """
    try:
        response = requests.get(f"{BASE_URL}/lanche_receita/{lanche_id}")

        if response.status_code == 200:
            receita_lista = response.json().get("receita", [])
            return {
                item["insumo_id"]: item["quantidade_base"] // 100
                for item in receita_lista
            }

        print(f"Erro ao buscar receita do lanche {lanche_id}: {response.status_code}")
        return {}

    except Exception as e:
        print(f"Erro de conexão ao buscar receita: {e}")
        return {}


def carregar_receita_base(lanche_id: int) -> dict:
    """
    Versão normalizada de listar_receita_lanche.

    Garante que todas as chaves são int e todos os valores são int > 0.
    Retorna {} se a receita estiver vazia ou em caso de erro.
    """
    try:
        dados_receita = listar_receita_lanche(lanche_id) or {}

        return {
            int(ing_id): int(qtd)
            for ing_id, qtd in dados_receita.items()
            if int(ing_id) > 0
        }

    except Exception as e:
        print(f"Erro ao normalizar receita base: {e}")
        return {}


# ---------------------------------------------------------------------------
# VENDAS DO GARÇOM (POR MESA)
# ---------------------------------------------------------------------------

def listar_vendas_mesa(token: str, numero_mesa) -> list:
    """
    Retorna as vendas registradas para uma mesa específica.
    Usado no resumo de fechamento de mesa do garçom.
    Retorna [] em caso de erro.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/vendas_garcom/{numero_mesa}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            return response.json().get("vendas", [])

        print(f"Erro ao buscar vendas da mesa {numero_mesa}: {response.text}")
        return []

    except Exception as e:
        print(f"Erro de conexão ao buscar vendas da mesa: {e}")
        return []