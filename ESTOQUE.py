import flet as ft
import openpyxl
from datetime import datetime

# Banco de dados em memória
estoque = {}

# Controle financeiro
total_vendido = 0.0
total_lucro = 0.0

# Histórico de vendas
historico_vendas = []


def main(page: ft.Page):
    global total_vendido, total_lucro

    page.title = "Sistema de Estoque"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"
    page.window.width = 950
    page.window.height = 700
    page.padding = 20

    # ========= CAMPOS =========
    codigo = ft.TextField(label="Código", width=140)
    nome = ft.TextField(label="Nome do Produto", width=230)

    preco_custo = ft.TextField(
        label="Preço de Custo (R$)",
        width=150,
        read_only=True  # custo automático
    )

    preco = ft.TextField(label="Preço de Venda (R$)", width=150)
    quantidade = ft.TextField(label="Quantidade", width=140)

    # ======= FUNÇÃO: custo automático =======
    def calcular_custo_automatico(e):
        try:
            preco_venda = float(preco.value)
            custo = preco_venda * 0.80  # 20% de lucro
            preco_custo.value = f"{custo:.2f}"
        except:
            preco_custo.value = ""
        page.update()

    preco.on_change = calcular_custo_automatico

    # ========= TABELA =========
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Custo")),
            ft.DataColumn(ft.Text("Preço")),
            ft.DataColumn(ft.Text("Qtd")),
            ft.DataColumn(ft.Text("Total")),
        ],
        rows=[],
        expand=True
    )

    # ========= RESUMO FINANCEIRO =========
    info_financeiro = ft.Container(
        content=ft.Text("", size=17, weight="bold"),
        padding=15,
        bgcolor="#f1f3f4",
        border_radius=10,
        width=350
    )

    # Atualizar tabela / financeiro
    def atualizar_interface():
        tabela.rows.clear()

        for cod, prod in estoque.items():
            total_prod = prod["preco"] * prod["qtd"]
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cod)),
                        ft.DataCell(ft.Text(prod["nome"])),
                        ft.DataCell(ft.Text(f"R$ {prod['custo']:.2f}")),
                        ft.DataCell(ft.Text(f"R$ {prod['preco']:.2f}")),
                        ft.DataCell(ft.Text(str(prod["qtd"]))),
                        ft.DataCell(ft.Text(f"R$ {total_prod:.2f}")),
                    ]
                )
            )

        if total_vendido > 0:
            perc = (total_lucro / total_vendido) * 100
        else:
            perc = 0

        info_financeiro.content.value = (
            f"💰 Total vendido: R$ {total_vendido:.2f}\n"
            f"📈 Lucro total: R$ {total_lucro:.2f}\n"
            f"🔥 Média de lucro: {perc:.2f}%"
        )

        page.update()

    # ========= FUNÇÃO: CADASTRAR =========
    def cadastrar(e):
        if not (codigo.value and nome.value and preco.value and quantidade.value and preco_custo.value):
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), open=True)
            return

        try:
            custo = float(preco_custo.value)
            valor = float(preco.value)
            qtd = int(quantidade.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Valores inválidos!"), open=True)
            return

        estoque[codigo.value] = {
            "nome": nome.value,
            "custo": custo,
            "preco": valor,
            "qtd": qtd
        }

        codigo.value = nome.value = preco.value = preco_custo.value = quantidade.value = ""

        page.snack_bar = ft.SnackBar(ft.Text("Produto cadastrado!"), open=True)
        atualizar_interface()

    # ========= FUNÇÃO: ENTRADA =========
    def entrada_estoque(e):
        cod = codigo.value

        if cod not in estoque:
            page.snack_bar = ft.SnackBar(ft.Text("Produto não encontrado!"), open=True)
            return

        try:
            qtd = int(quantidade.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Quantidade inválida!"), open=True)
            return

        estoque[cod]["qtd"] += qtd
        page.snack_bar = ft.SnackBar(ft.Text("Entrada registrada!"), open=True)
        atualizar_interface()

    # ========= FUNÇÃO: VENDA =========
    def saida_estoque(e):
        global total_vendido, total_lucro

        cod = codigo.value

        if cod not in estoque:
            page.snack_bar = ft.SnackBar(ft.Text("Produto não encontrado!"), open=True)
            return

        try:
            qtd = int(quantidade.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Quantidade inválida!"), open=True)
            return

        if qtd > estoque[cod]["qtd"]:
            page.snack_bar = ft.SnackBar(ft.Text("Estoque insuficiente!"), open=True)
            return

        preco_venda = estoque[cod]["preco"]
        custo = estoque[cod]["custo"]

        valor_venda = preco_venda * qtd
        lucro_venda = (preco_venda - custo) * qtd

        total_vendido += valor_venda
        total_lucro += lucro_venda

        estoque[cod]["qtd"] -= qtd

        # Registrar histórico
        historico_vendas.append({
            "codigo": cod,
            "nome": estoque[cod]["nome"],
            "quantidade": qtd,
            "valor_total": valor_venda,
            "lucro": lucro_venda,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

        page.snack_bar = ft.SnackBar(ft.Text("Venda registrada!"), open=True)
        atualizar_interface()

    # ========= LAYOUT =========
    page.add(
        ft.Text("📦 Controle de Estoque", size=34, weight="bold"),
        ft.Divider(height=20),

        ft.Container(
            padding=20,
            bgcolor="#f8f9fa",
            border_radius=12,
            content=ft.Column([
                ft.Text("Cadastro de Produtos", size=20, weight="bold"),
                ft.Row([codigo, nome, preco_custo, preco, quantidade], wrap=True),
                ft.Row([
                    ft.ElevatedButton("Cadastrar", icon="add", on_click=cadastrar),
                    ft.ElevatedButton("Entrada", icon="arrow_downward", on_click=entrada_estoque),
                    ft.ElevatedButton("Venda", icon="shopping_cart", on_click=saida_estoque),
                ], spacing=20),
            ])
        ),

        ft.Divider(height=25),

        ft.Text("📑 Tabela de Produtos", size=22, weight="bold"),
        tabela,

        ft.Divider(height=25),

        ft.Text("📊 Resumo Financeiro", size=22, weight="bold"),
        info_financeiro,
    )

    atualizar_interface()


ft.app(target=main)

import flet as ft

# Estrutura do estoque (simples em memória)
estoque = {}


def main(page: ft.Page):
    page.title = "Controle de Estoque - Flet"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"

    # Campos de cadastro
    codigo = ft.TextField(label="Código", width=150)
    nome = ft.TextField(label="Nome do Produto", width=250)
    preco = ft.TextField(label="Preço (R$)", width=120)
    quantidade = ft.TextField(label="Quantidade", width=120)

    # Tabela do estoque
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Preço")),
            ft.DataColumn(ft.Text("Quantidade")),
            ft.DataColumn(ft.Text("Valor Total")),
        ],
        rows=[],
        expand=True
    )

    # Atualiza a tabela visual
    def atualizar_tabela():
        tabela.rows.clear()

        for cod, prod in estoque.items():
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cod)),
                        ft.DataCell(ft.Text(prod["nome"])),
                        ft.DataCell(ft.Text(f'R$ {prod["preco"]:.2f}')),
                        ft.DataCell(ft.Text(str(prod["qtd"]))),
                        ft.DataCell(ft.Text(f'R$ {prod["preco"] * prod["qtd"]:.2f}')),
                    ]
                )
            )

        page.update()

    # Botão cadastrar
    def cadastrar(e):
        if codigo.value == "" or nome.value == "" or preco.value == "" or quantidade.value == "":
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), open=True)
            page.update()
            return

        try:
            preco_value = float(preco.value)
            qtd_value = int(quantidade.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Preço ou quantidade inválidos!"), open=True)
            page.update()
            return

        estoque[codigo.value] = {
            "nome": nome.value,
            "preco": preco_value,
            "qtd": qtd_value
        }

        page.snack_bar = ft.SnackBar(ft.Text("Produto cadastrado!"), open=True)

        # Limpa os campos
        codigo.value = nome.value = preco.value = quantidade.value = ""

        atualizar_tabela()
        page.update()

    # Entrada de estoque
    def entrada_estoque(e):
        cod = codigo.value

        if cod not in estoque:
            page.snack_bar = ft.SnackBar(ft.Text("Produto não encontrado!"), open=True)
            return
        
        try:
            qtd = int(quantidade.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Quantidade inválida!"), open=True)
            return

        estoque[cod]["qtd"] += qtd
        page.snack_bar = ft.SnackBar(ft.Text("Entrada registrada!"), open=True)
        atualizar_tabela()

    # Saída de estoque
    def saida_estoque(e):
        cod = codigo.value

        if cod not in estoque:
            page.snack_bar = ft.SnackBar(ft.Text("Produto não encontrado!"), open=True)
            return
        
        try:
            qtd = int(quantidade.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Quantidade inválida!"), open=True)
            return

        if qtd > estoque[cod]["qtd"]:
            page.snack_bar = ft.SnackBar(ft.Text("Estoque insuficiente!"), open=True)
            return

        estoque[cod]["qtd"] -= qtd
        page.snack_bar = ft.SnackBar(ft.Text("Saída registrada!"), open=True)
        atualizar_tabela()

    # Layout principal ---
    page.add(
        ft.Text("📦 Sistema de Controle de Estoque", size=30, weight="bold"),
        ft.Divider(height=2),

        ft.Row(
            [codigo, nome, preco, quantidade],
            wrap=True
        ),

        ft.Row(
            [
                ft.ElevatedButton("Cadastrar Produto", on_click=cadastrar),
                ft.ElevatedButton("Entrada", on_click=entrada_estoque),
                ft.ElevatedButton("Saída", on_click=saida_estoque)
            ],
            spacing=20
        ),

        ft.Divider(height=20, color="transparent"),

        ft.Text("📑 Produtos cadastrados", size=22, weight="bold"),
        tabela
    )

    atualizar_tabela()


# Start
ft.app(target=main)
