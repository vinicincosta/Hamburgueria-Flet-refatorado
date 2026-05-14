"""
theme.py — Design System do Royal Burger
Centraliza todas as constantes visuais do app:
  cores, raios, sombras, estilos de texto e helpers de componentes.
Importado pelo app.py — nenhuma lógica de negócio aqui.
"""
import flet as ft
from flet.core.colors import Colors

# ──────────────────────────────────────────────
# PALETA DE CORES
# ──────────────────────────────────────────────
BG          = "#0D1117"       # fundo principal (quase preto)
BG_CARD     = "#161E25"       # cards e painéis
BG_CARD2    = "#1A2230"       # segundo nível de card
BG_INPUT    = "#1E2A36"       # campos de texto
ACCENT      = "#DAA520"       # dourado — identidade
ACCENT_DARK = "#B8860B"
ACCENT_LIGHT= "#F1C94A"
BLUE        = "#3B82F6"
RED         = "#EF4444"
GREEN       = "#22C55E"
TEXT        = "#F0F4F8"
MUTED       = "#8A9BB0"
DIM         = "#4A5568"
BORDER      = "#FFFFFF14"     # rgba(255,255,255,0.08)
BORDER_AC   = "#DAA52059"     # rgba(218,165,32,0.35)

# ──────────────────────────────────────────────
# STATUS BADGES
# ──────────────────────────────────────────────
STATUS_ENVIADO   = "#22C55E"
STATUS_PENDENTE  = "#EF4444"
STATUS_PREPARO   = "#F97316"

# ──────────────────────────────────────────────
# RAIOS
# ──────────────────────────────────────────────
R_SM = 8
R_MD = 14
R_LG = 20
R_XL = 28

# ──────────────────────────────────────────────
# HELPERS DE ESTILO
# ──────────────────────────────────────────────

def sombra(cor=None, blur=20, spread=1, dy=4):
    """Retorna um BoxShadow padrão."""
    return ft.BoxShadow(
        blur_radius=blur, spread_radius=spread,
        color=cor or ft.Colors.with_opacity(0.5, "#000000"),
        offset=ft.Offset(0, dy)
    )

def sombra_dourada():
    return ft.BoxShadow(
        blur_radius=24, spread_radius=2,
        color=ft.Colors.with_opacity(0.3, ACCENT),
        offset=ft.Offset(0, 6)
    )

def borda(color=BORDER, width=1):
    return ft.border.all(width, color)

def borda_ac():
    return ft.border.all(1, BORDER_AC)

def estilo_btn_primario(large=False):
    """Botão dourado principal."""
    pad = 18 if large else 14
    return ft.ButtonStyle(
        bgcolor=ACCENT,
        color="#111111",
        padding=pad,
        overlay_color=ft.Colors.with_opacity(0.15, "#FFFFFF"),
        shape=ft.RoundedRectangleBorder(radius=R_MD),
        shadow_color=ft.Colors.with_opacity(0.35, ACCENT),
        elevation=4,
    )

def estilo_btn_secundario():
    """Botão contornado."""
    return ft.ButtonStyle(
        color=ACCENT,
        padding=14,
        side=ft.BorderSide(1, ACCENT),
        shape=ft.RoundedRectangleBorder(radius=R_MD),
        overlay_color=ft.Colors.with_opacity(0.08, ACCENT),
    )

def estilo_btn_ghost():
    """Botão transparente para ações secundárias."""
    return ft.ButtonStyle(
        color=MUTED,
        padding=12,
        shape=ft.RoundedRectangleBorder(radius=R_SM),
        overlay_color=ft.Colors.with_opacity(0.06, "#FFFFFF"),
    )

def estilo_btn_perigo():
    """Botão vermelho para remoção."""
    return ft.ButtonStyle(
        color=RED,
        padding=10,
        side=ft.BorderSide(1, RED),
        shape=ft.RoundedRectangleBorder(radius=R_SM),
        overlay_color=ft.Colors.with_opacity(0.08, RED),
    )

def estilo_input(label: str, hint: str = "", password: bool = False, width: int = None):
    """Campo de texto padronizado."""
    kw = dict(
        label=label,
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        label_style=ft.TextStyle(color=MUTED, size=13),
        hint_style=ft.TextStyle(color=DIM),
        border_radius=R_MD,
        cursor_color=ACCENT,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )
    if width:
        kw["width"] = width
    return ft.TextField(**kw)

def chip_status(label: str, cor: str):
    """Badge de status pequeno."""
    return ft.Container(
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_700, color=cor),
        bgcolor=ft.Colors.with_opacity(0.15, cor),
        border=ft.border.all(1, ft.Colors.with_opacity(0.35, cor)),
        border_radius=999,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )

def divider_dourado():
    return ft.Divider(height=1, color=BORDER_AC, thickness=1)

def app_bar(titulo, leading=None, actions=None, rota=None):
    """AppBar padronizada para todas as telas."""
    return ft.AppBar(
        titulo,
        title=ft.Text(
            style=ft.TextStyle(
                size=18,
                weight=ft.FontWeight.W_700,
                color=TEXT,
                letter_spacing=0.3,
            ),

            size=18,
            weight=ft.FontWeight.W_700,
            color=TEXT
        ),
        center_title=True,
        bgcolor=BG_CARD,
        color=TEXT,

        actions=actions or [],
        elevation=0,
        surface_tint_color="transparent",
    )
def logo_widget(width=44):
    return ft.Image(src="imgdois.png", width=width, fit=ft.ImageFit.CONTAIN)

def btn_voltar(page, rota):
    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
        icon_color=MUTED,
        on_click=lambda _: page.go(rota),
        tooltip="Voltar",
    )

def btn_logout_icon(on_click):
    return ft.IconButton(
        icon=ft.Icons.LOGOUT_ROUNDED,
        icon_color=RED,
        icon_size=22,
        on_click=on_click,
        tooltip="Sair",
    )

def secao_titulo(texto: str, subtexto: str = ""):
    col = [ft.Text(texto, size=22, weight=ft.FontWeight.W_800, color=TEXT)]
    if subtexto:
        col.append(ft.Text(subtexto, size=13, color=MUTED))
    return ft.Column(col, spacing=2)
