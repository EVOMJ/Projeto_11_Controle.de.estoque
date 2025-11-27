
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
