"""
components.py — Componentes reutilizáveis do Royal Burger
Cada função retorna um widget Flet pronto para uso.
Nenhuma lógica de negócio aqui — apenas UI.
"""
import flet as ft
from theme import (
    BG, BG_CARD, BG_CARD2, BG_INPUT, ACCENT, ACCENT_DARK, ACCENT_LIGHT,
    BLUE, RED, GREEN, TEXT, MUTED, DIM, BORDER, BORDER_AC,
    R_SM, R_MD, R_LG, R_XL, STATUS_ENVIADO, STATUS_PENDENTE, STATUS_PREPARO,
    sombra, sombra_dourada, borda, borda_ac, chip_status, estilo_btn_primario,
    estilo_btn_secundario, estilo_btn_ghost, estilo_btn_perigo, divider_dourado,
)

# URLs de imagem do Unsplash — específicas por categoria
IMAGENS_LANCHE = {
    "default": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80",
    "x-burguer": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&q=80",
    "x-bacon": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=400&q=80",
    "frango": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400&q=80",
    "vegano": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=400&q=80",
}

IMAGENS_BEBIDA = {
    "default": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80",
    "coca": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80",
    "suco": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&q=80",
    "agua": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&q=80",
    "cerveja": "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400&q=80",
}


def _get_img_lanche(nome: str) -> str:
    nome_l = nome.lower()
    for k, v in IMAGENS_LANCHE.items():
        if k in nome_l:
            return v
    return IMAGENS_LANCHE["default"]


def _get_img_bebida(nome: str) -> str:
    nome_l = nome.lower()
    for k, v in IMAGENS_BEBIDA.items():
        if k in nome_l:
            return v
    return IMAGENS_BEBIDA["default"]


# ──────────────────────────────────────────────
# CARD DE LANCHE (cardápio)
# ──────────────────────────────────────────────
def card_lanche(lanche: dict, on_action, label_btn="Adicionar", disabled=False):
    """
    Card moderno de lanche para cardápio delivery/presencial.
    on_action: callback chamado ao clicar no botão.
    """
    nome     = lanche.get("nome_lanche", "Lanche")
    valor    = float(lanche.get("valor_lanche", 0))
    descricao= lanche.get("descricao_lanche", "")
    disponivel = lanche.get("disponivel", True) and not disabled

    img_url  = _get_img_lanche(nome)

    return ft.Container(
        border_radius=R_LG,
        bgcolor=BG_CARD,
        border=borda_ac() if disponivel else borda(BORDER),
        shadow=sombra_dourada() if disponivel else sombra(),
        opacity=1.0 if disponivel else 0.45,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                # Imagem do produto
                ft.Container(
                    height=160,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border_radius=ft.border_radius.only(top_left=R_LG, top_right=R_LG),
                    content=ft.Image(
                        src=img_url,
                        fit=ft.ImageFit.COVER,
                        width=9999,
                        height=160,
                        error_content=ft.Container(
                            bgcolor=BG_CARD2, height=160,
                            content=ft.Icon(ft.Icons.FASTFOOD, color=MUTED, size=48),
                        ),
                    ),
                ),
                # Corpo do card
                ft.Container(
                    padding=ft.padding.all(16),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                nome, size=16, weight=ft.FontWeight.W_700,
                                color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                descricao, size=12, color=MUTED,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                            ) if descricao else ft.Container(height=0),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        f"R$ {valor:.2f}",
                                        size=18, weight=ft.FontWeight.W_800, color=ACCENT,
                                    ),
                                    ft.ElevatedButton(
                                        label_btn if disponivel else "Indisponível",
                                        disabled=not disponivel,
                                        on_click=on_action if disponivel else None,
                                        style=estilo_btn_primario() if disponivel
                                              else ft.ButtonStyle(
                                                  bgcolor=DIM, color=MUTED,
                                                  shape=ft.RoundedRectangleBorder(radius=R_SM)
                                              ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# CARD DE BEBIDA (cardápio)
# ──────────────────────────────────────────────
def card_bebida(bebida: dict, on_action, label_btn="Adicionar"):
    """Card moderno de bebida para cardápio."""
    nome       = bebida.get("nome_bebida", "Bebida")
    valor      = float(bebida.get("valor", 0))
    descricao  = bebida.get("descricao", "")
    disponivel = bebida.get("status_bebida", True)

    img_url = _get_img_bebida(nome)

    return ft.Container(
        border_radius=R_LG,
        bgcolor=BG_CARD,
        border=borda(BLUE + "59") if disponivel else borda(BORDER),
        shadow=ft.BoxShadow(
            blur_radius=20, spread_radius=1,
            color=ft.Colors.with_opacity(0.25, BLUE),
            offset=ft.Offset(0, 4)
        ) if disponivel else sombra(),
        opacity=1.0 if disponivel else 0.45,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    height=140,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border_radius=ft.border_radius.only(top_left=R_LG, top_right=R_LG),
                    content=ft.Image(
                        src=img_url,
                        fit=ft.ImageFit.COVER,
                        width=9999, height=140,
                        error_content=ft.Container(
                            bgcolor=BG_CARD2, height=140,
                            content=ft.Icon(ft.Icons.LOCAL_DRINK, color=MUTED, size=40),
                        ),
                    ),
                ),
                ft.Container(
                    padding=ft.padding.all(14),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                nome, size=15, weight=ft.FontWeight.W_700,
                                color=TEXT, max_lines=1
                            ),
                            ft.Text(descricao, size=12, color=MUTED, max_lines=2)
                            if descricao else ft.Container(height=0),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        f"R$ {valor:.2f}",
                                        size=16, weight=ft.FontWeight.W_800, color=BLUE,
                                    ),
                                    ft.ElevatedButton(
                                        label_btn if disponivel else "Indisponível",
                                        disabled=not disponivel,
                                        on_click=on_action if disponivel else None,
                                        style=ft.ButtonStyle(
                                            bgcolor=BLUE if disponivel else DIM,
                                            color="#FFFFFF" if disponivel else MUTED,
                                            shape=ft.RoundedRectangleBorder(radius=R_SM),
                                            padding=10,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# CARD DE ITEM DO CARRINHO
# ──────────────────────────────────────────────
def card_item_carrinho(
    nome: str, valor: float, tipo: str,
    on_remover=None, on_obs=None,
    extra_badge: str = None,
):
    """Card de item no carrinho — lanche ou bebida."""
    is_lanche = tipo == "lanche"
    img_url   = _get_img_lanche(nome) if is_lanche else _get_img_bebida(nome)
    cor_valor = ACCENT if is_lanche else BLUE

    acoes = []
    if on_obs and is_lanche:
        acoes.append(
            ft.ElevatedButton(
                "Obs", icon=ft.Icons.EDIT_NOTE_ROUNDED,
                on_click=on_obs, style=estilo_btn_secundario(),
            )
        )
    if on_remover:
        acoes.append(
            ft.OutlinedButton(
                "Remover", icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                on_click=on_remover, style=estilo_btn_perigo(),
            )
        )

    return ft.Container(
        bgcolor=BG_CARD,
        border_radius=R_MD,
        border=borda(),
        shadow=sombra(blur=12),
        padding=ft.padding.all(14),
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=72, height=72,
                    border_radius=R_MD,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=img_url, fit=ft.ImageFit.COVER,
                        width=72, height=72,
                        error_content=ft.Container(
                            bgcolor=BG_CARD2,
                            content=ft.Icon(
                                ft.Icons.FASTFOOD if is_lanche else ft.Icons.LOCAL_DRINK,
                                color=MUTED, size=32,
                            ),
                        ),
                    ),
                ),
                ft.Column(
                    expand=True, spacing=6,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    nome, size=15, weight=ft.FontWeight.W_700,
                                    color=TEXT, expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS, max_lines=1,
                                ),
                                chip_status(extra_badge, GREEN) if extra_badge else ft.Container(),
                            ],
                        ),
                        ft.Text(
                            f"R$ {valor:.2f}",
                            size=15, weight=ft.FontWeight.W_800, color=cor_valor,
                        ),
                        ft.Row(spacing=8, controls=acoes),
                    ],
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# CARD DE MESA (garçom)
# ──────────────────────────────────────────────
def card_mesa(numero: str, n_itens: int, tem_pendente: bool, on_tap):
    """Card de mesa para a tela do garçom."""
    ocupada = n_itens > 0
    cor     = ACCENT if ocupada else BG_CARD2
    cor_txt = "#111111" if ocupada else MUTED
    icone   = ft.Icons.TABLE_RESTAURANT_ROUNDED

    return ft.GestureDetector(
        on_tap=on_tap,
        content=ft.Container(
            width=100, height=100,
            border_radius=R_MD,
            bgcolor=cor if ocupada else BG_CARD,
            border=borda_ac() if ocupada else borda(),
            shadow=sombra_dourada() if ocupada else sombra(blur=8),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Icon(icone, color=cor_txt, size=28),
                    ft.Text(
                        f"Mesa {numero}",
                        size=13, weight=ft.FontWeight.W_700, color=cor_txt,
                    ),
                    ft.Text(
                        f"{n_itens} itens" if ocupada else "Livre",
                        size=11, color=cor_txt,
                    ),
                    chip_status("Pendente", RED) if tem_pendente else ft.Container(height=0),
                ],
            ),
        ),
    )


# ──────────────────────────────────────────────
# CARD DE ITEM DO CARRINHO GARÇOM
# ──────────────────────────────────────────────
def card_item_garcom(
    item: dict, index_real: int,
    on_remover=None, on_obs=None,
):
    """Card de item no carrinho do garçom com badge de status."""
    is_lanche = "nome_lanche" in item
    nome      = item.get("nome_lanche") or item.get("nome_bebida", "Item")
    valor     = float(item.get("valor_lanche", 0) or item.get("valor", 0))
    enviado   = item.get("enviado", False)
    img_url   = _get_img_lanche(nome) if is_lanche else _get_img_bebida(nome)
    cor_borda = GREEN if enviado else STATUS_PENDENTE

    acoes = []
    if not enviado:
        if on_remover:
            acoes.append(
                ft.OutlinedButton(
                    "Remover", icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    on_click=lambda e: on_remover(index_real),
                    style=estilo_btn_perigo(),
                )
            )
        if on_obs and is_lanche:
            acoes.append(
                ft.ElevatedButton(
                    "Obs", icon=ft.Icons.EDIT_NOTE_ROUNDED,
                    on_click=lambda e: on_obs(item),
                    style=estilo_btn_secundario(),
                )
            )

    return ft.Container(
        bgcolor=BG_CARD,
        border_radius=R_MD,
        border=ft.border.all(1, cor_borda + "66"),
        shadow=sombra(cor=cor_borda + "33", blur=14),
        padding=ft.padding.all(14),
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=70, height=70, border_radius=R_MD,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=img_url, fit=ft.ImageFit.COVER, width=70, height=70,
                        error_content=ft.Container(
                            bgcolor=BG_CARD2,
                            content=ft.Icon(
                                ft.Icons.FASTFOOD if is_lanche else ft.Icons.LOCAL_DRINK,
                                color=MUTED, size=30,
                            ),
                        ),
                    ),
                ),
                ft.Column(
                    expand=True, spacing=6,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    nome, size=15, weight=ft.FontWeight.W_700,
                                    color=TEXT, expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS, max_lines=1,
                                ),
                                chip_status("✔ Enviado", GREEN) if enviado
                                else chip_status("● Pendente", RED),
                            ],
                        ),
                        ft.Text(
                            f"R$ {valor:.2f}",
                            size=14, weight=ft.FontWeight.W_700, color=ACCENT,
                        ),
                        ft.Row(spacing=8, controls=acoes) if acoes else ft.Container(height=0),
                    ],
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# CARD DE INGREDIENTE (observações)
# ──────────────────────────────────────────────
def card_ingrediente(nome: str, preco: float, txt_ctrl, on_aumentar, on_diminuir):
    """Card de controle de quantidade de ingrediente."""
    return ft.Container(
        bgcolor=BG_CARD,
        border_radius=R_MD,
        border=borda(),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2, expand=True,
                    controls=[
                        ft.Text(nome, size=14, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.Text(f"R$ {preco:.2f}/un", size=12, color=MUTED),
                    ],
                ),
                ft.Row(
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED,
                            icon_color=RED, icon_size=22,
                            on_click=on_diminuir,
                        ),
                        ft.Container(
                            width=36, height=36,
                            bgcolor=BG_CARD2, border_radius=R_SM,
                            alignment=ft.alignment.center,
                            content=txt_ctrl,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                            icon_color=GREEN, icon_size=22,
                            on_click=on_aumentar,
                        ),
                    ],
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# CARD DE PEDIDO NO HISTÓRICO
# ──────────────────────────────────────────────
def card_historico(data: str, itens: list, status: int, status_texto: str):
    """Card de grupo de pedidos no histórico do cliente."""
    cores = {0: GREEN, 1: ACCENT, 2: RED}
    cor   = cores.get(status, MUTED)
    progresso = [0.33, 0.66, 1.0][min(status, 2)]

    return ft.Container(
        bgcolor=BG_CARD,
        border_radius=R_LG,
        border=ft.border.all(1, cor + "44"),
        shadow=sombra(cor=cor + "22", blur=16),
        padding=ft.padding.all(18),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, color=cor, size=20),
                                ft.Text(data, size=14, weight=ft.FontWeight.W_600, color=TEXT),
                            ],
                        ),
                        chip_status(status_texto, cor),
                    ],
                ),
                divider_dourado(),
                *[ft.Text(f"• {i}", size=13, color=MUTED) for i in itens],
                ft.ProgressBar(
                    value=progresso, color=cor,
                    bgcolor=ft.Colors.with_opacity(0.15, cor),
                    bar_height=6, border_radius=999,
                ),
            ],
        ),
    )


# ──────────────────────────────────────────────
# TELA DE ESTADO VAZIO
# ──────────────────────────────────────────────
def estado_vazio(icone, titulo: str, subtitulo: str = ""):
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(icone, size=64, color=DIM),
                ft.Text(titulo, size=18, weight=ft.FontWeight.W_700, color=MUTED),
                ft.Text(subtitulo, size=13, color=DIM) if subtitulo else ft.Container(),
            ],
        ),
    )


# ──────────────────────────────────────────────
# RESUMO ITEM (fechamento de mesa)
# ──────────────────────────────────────────────
def resumo_item(nome: str, valor: float, tipo: str = "lanche"):
    icone = ft.Icons.FASTFOOD_ROUNDED if tipo == "lanche" else ft.Icons.LOCAL_DRINK_ROUNDED
    cor   = ACCENT if tipo == "lanche" else BLUE
    return ft.Container(
        bgcolor=BG_CARD2,
        border_radius=R_SM,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(icone, color=cor, size=16),
                        ft.Text(nome, size=14, weight=ft.FontWeight.W_600, color=TEXT),
                    ],
                ),
                ft.Text(f"R$ {valor:.2f}", size=14, weight=ft.FontWeight.W_700, color=cor),
            ],
        ),
    )
