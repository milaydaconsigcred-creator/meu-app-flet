import flet as ft
import requests
import json

URL_BASE = "https://restaurante-alves-default-rtdb.firebaseio.com/"

def main(page: ft.Page):
    page.title = "Alves Gestão"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    
    # --- VARIÁVEIS E FUNÇÕES DE APOIO ---
    lista_estoque = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def carregar_estoque(e=None):
        lista_estoque.controls.clear()
        try:
            res = requests.get(f"{URL_BASE}/produtos.json").json()
            if res:
                for cod, d in res.items():
                    est_atual = float(d.get('estoque', 0))
                    est_min = float(d.get('minimo', 0))
                    cor_texto = ft.colors.RED_ACCENT if est_atual <= est_min else ft.colors.WHITE
                    
                    lista_estoque.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.INVENTORY_2, color=cor_texto),
                            title=ft.Text(f"{d['nome']}", color=cor_texto, weight="bold"),
                            subtitle=ft.Text(f"Qtd: {est_atual} | Mín: {est_min}"),
                            trailing=ft.Text(f"R$ {d['preco']:.2f}"),
                            on_click=lambda _, c=cod: mudar_para_scanner(c)
                        )
                    )
            page.update()
        except:
            pass

    def mudar_para_scanner(codigo):
        txt_cod.value = codigo
        tabs.selected_index = 0 # Volta para a aba de movimento
        page.update()

    def registrar_movimento(tipo):
        if not txt_cod.value or not txt_qtd.value:
            return
        
        res = requests.get(f"{URL_BASE}/produtos/{txt_cod.value}.json").json()
        if res:
            try:
                qtd_informada = float(txt_qtd.value.replace(",", "."))
                estoque_atual = float(res.get('estoque', 0))
                
                if tipo == "entrada":
                    novo_total = estoque_atual + qtd_informada
                    msg = f"Reposição de {qtd_informada} un. realizada!"
                else:
                    novo_total = estoque_atual - qtd_informada
                    msg = f"Baixa de {qtd_informada} un. realizada!"
                
                requests.patch(f"{URL_BASE}/produtos/{txt_cod.value}.json", 
                               data=json.dumps({"estoque": novo_total}))
                
                txt_cod.value = ""
                txt_qtd.value = "1"
                carregar_estoque()
                
                page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.colors.GREEN_700)
                page.snack_bar.open = True
                page.update()
            except:
                pass
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Produto não encontrado!"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()

    # --- COMPONENTES DA ABA 1 (MOVIMENTAÇÃO) ---
    txt_cod = ft.TextField(label="Código do Produto", prefix_icon=ft.icons.BARCODE_READER)
    txt_qtd = ft.TextField(label="Quantidade", value="1", keyboard_type=ft.KeyboardType.NUMBER)
    
    aba_movimento = ft.Column([
        ft.Text("Lançar Movimentação", size=20, weight="bold"),
        txt_cod,
        txt_qtd,
        ft.Row([
            ft.ElevatedButton(
                "REPOSIÇÃO (+)", 
                icon=ft.icons.ADD_CIRCLE, 
                on_click=lambda _: registrar_movimento("entrada"),
                bgcolor=ft.colors.GREEN_700,
                color=ft.colors.WHITE,
                expand=True
            ),
            ft.ElevatedButton(
                "BAIXA (-)", 
                icon=ft.icons.REMOVE_CIRCLE, 
                on_click=lambda _: registrar_movimento("saida"),
                bgcolor=ft.colors.RED_700,
                color=ft.colors.WHITE,
                expand=True
            ),
        ]),
        ft.Divider(),
        ft.Text("Dica: Use o scanner para preencher o código.", size=12, italic=True)
    ], scroll=ft.ScrollMode.AUTO)

    # --- COMPONENTES DA ABA 2 (LISTA / CONSULTA) ---
    aba_lista = ft.Column([
        ft.Row([
            ft.Text("Situação do Estoque", size=20, weight="bold"),
            ft.IconButton(ft.icons.REFRESH, on_click=carregar_estoque)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        lista_estoque
    ], expand=True)

    # --- ORGANIZAÇÃO DAS ABAS ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Lançar", icon=ft.icons.ADJUST, content=aba_movimento),
            ft.Tab(text="Estoque", icon=ft.icons.LIST_ALT, content=aba_lista),
        ],
        expand=True
    )

    page.add(tabs)
    carregar_estoque()

ft.app(target=main)