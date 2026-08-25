import flet as ft
import os
import datetime
import asyncio
from database import init_db, salvar_historico_usuario
from api_service import atualizar_dados
from estatisticas import gerar_combinacoes, REGRAS

def main(page: ft.Page):
    # Inicializa banco de dados
    init_db()

    # Configurações da Página
    page.title = "Gerador de Loterias"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.window.width = 400
    page.window.height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Loader (substituto do antigo page.splash)
    splash = ft.ProgressBar(visible=False)
    page.overlay.append(splash)

    # Cores
    COR_CABECALHO = "#0D47A1"
    COR_BOTAO_GERAR = "#00C853"
    COR_DEZENAS = "#FF9800"
    COR_TREVOS = "#4CAF50" # Verde para trevos

    # Variável de estado para resultados gerados na sessão
    resultados_sessao = []

    # Componentes UI
    header = ft.Container(
        content=ft.Text("App Loterias", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=COR_CABECALHO,
        padding=20,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        width=float('inf')
    )

    def on_modalidade_change(e):
        mod = dropdown_modalidade.value
        regra = REGRAS[mod]
        min_d = regra['min_dezenas']
        max_d = regra['max_dezenas']
        
        dropdown_tamanho.options = [
            ft.dropdown.Option(key=str(i), text=f"{i} dezenas") for i in range(min_d, max_d + 1)
        ]
        dropdown_tamanho.value = str(min_d)
        page.update()

    dropdown_modalidade = ft.Dropdown(
        label="Escolha a Loteria",
        options=[
            ft.dropdown.Option(key="megasena", text="Mega-Sena"),
            ft.dropdown.Option(key="lotofacil", text="Lotofácil"),
            ft.dropdown.Option(key="maismilionaria", text="Mais Milionária"),
        ],
        value="megasena",
        width=float('inf'),
        on_select=on_modalidade_change
    )

    dropdown_tamanho = ft.Dropdown(
        label="Tamanho da Aposta",
        options=[
            ft.dropdown.Option(key=str(i), text=f"{i} dezenas") for i in range(6, 21)
        ],
        value="6",
        width=float('inf')
    )

    txt_dezenas_fixas = ft.TextField(
        label="Dezenas Fixas (opcional, separadas por vírgula)",
        hint_text="Ex: 4, 15, 33",
        width=float('inf')
    )

    switch_quentes = ft.Switch(label="Usar números mais sorteados?", value=False)
    
    txt_quantidade = ft.TextField(
        label="Quantidade de Combinações",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=float('inf')
    )

    container_resultados = ft.Column(spacing=10, width=float('inf'))

    def mostrar_snack(mensagem: str):
        snack = ft.SnackBar(content=ft.Text(mensagem), open=True)
        page.overlay.append(snack)
        page.update()

    async def btn_gerar_click(e):
        modalidade = dropdown_modalidade.value
        usar_quentes = switch_quentes.value
        tamanho_aposta = int(dropdown_tamanho.value)
        
        dezenas_fixas_str = txt_dezenas_fixas.value.strip() if txt_dezenas_fixas.value else ""
        dezenas_fixas = []
        if dezenas_fixas_str:
            try:
                parts = [p.strip() for p in dezenas_fixas_str.split(',') if p.strip()]
                dezenas_fixas = [int(p) for p in parts]
                
                regra = REGRAS[modalidade]
                for d in dezenas_fixas:
                    if d < 1 or d > regra['total_dezenas']:
                        mostrar_snack(f"A dezena {d} é inválida para a loteria escolhida.")
                        return
                
                if len(set(dezenas_fixas)) != len(dezenas_fixas):
                    mostrar_snack("Existem dezenas fixas duplicadas.")
                    return
                
                if len(dezenas_fixas) > tamanho_aposta:
                    mostrar_snack(f"Você escolheu {len(dezenas_fixas)} dezenas fixas, mas o tamanho da aposta é {tamanho_aposta}.")
                    return
            except ValueError:
                mostrar_snack("Formato inválido nas dezenas fixas. Use apenas números separados por vírgula.")
                return
        
        try:
            qtd = int(txt_quantidade.value)
            if qtd < 1 or qtd > 10:
                mostrar_snack("Digite uma quantidade entre 1 e 10.")
                return
        except ValueError:
            mostrar_snack("Quantidade inválida.")
            return

        # Mostra progress bar
        splash.visible = True
        btn_gerar.disabled = True
        page.update()

        try:
            # Tenta atualizar os dados na API assincronamente (ou usa fallback)
            await atualizar_dados(modalidade)
            
            # Gera as combinações
            resultados = gerar_combinacoes(modalidade, qtd, usar_quentes, dezenas_fixas, tamanho_aposta)
            
            container_resultados.controls.clear()
            
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for index, res in enumerate(resultados):
                dezenas = res['dezenas']
                trevos = res['trevos']
                
                # Salva no banco de dados o histórico do usuário
                salvar_historico_usuario(modalidade, data_atual, dezenas, trevos)
                
                # Adiciona na sessão para exportação
                resultados_sessao.append({
                    'modalidade': modalidade,
                    'dezenas': dezenas,
                    'trevos': trevos
                })
                
                # Monta a visualização (Chips)
                linha_dezenas = ft.Row(wrap=True, spacing=5)
                for d in dezenas:
                    linha_dezenas.controls.append(
                        ft.Container(
                            content=ft.Text(d, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=COR_DEZENAS,
                            shape=ft.BoxShape.CIRCLE,
                            padding=10,
                            width=40,
                            height=40,
                            alignment=ft.Alignment.CENTER
                        )
                    )
                    
                linha_trevos = None
                if trevos:
                    linha_trevos = ft.Row(wrap=True, spacing=5)
                    linha_trevos.controls.append(ft.Text("Trevos: ", weight=ft.FontWeight.BOLD))
                    for t in trevos:
                        linha_trevos.controls.append(
                            ft.Container(
                                content=ft.Text(t, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=COR_TREVOS,
                                shape=ft.BoxShape.CIRCLE,
                                padding=10,
                                width=40,
                                height=40,
                                alignment=ft.Alignment.CENTER
                            )
                        )
                
                cartao = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Jogo {index+1}", weight=ft.FontWeight.BOLD),
                        linha_dezenas,
                        linha_trevos if linha_trevos else ft.Container()
                    ]),
                    padding=15,
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.WHITE24)
                )
                
                container_resultados.controls.append(cartao)

        except Exception as ex:
            mostrar_snack(f"Erro ao gerar: {str(ex)}")
        finally:
            splash.visible = False
            btn_gerar.disabled = False
            page.update()

    def btn_exportar_click(e):
        if not resultados_sessao:
            mostrar_snack("Nenhum resultado gerado para exportar nesta sessão.")
            return
            
        try:
            # Obtém caminho de storage do app (seguro no mobile)
            # Em desktop ele irá para a pasta temporária ou de dados do usuário dependendo do SO
            import tempfile
            path = tempfile.gettempdir()
                
            arquivo_path = os.path.join(path, "minhas_combinacoes.txt")
            
            with open(arquivo_path, "w", encoding="utf-8") as f:
                f.write("--- Minhas Combinações de Loterias ---\n\n")
                for item in resultados_sessao:
                    linha = f"Modalidade: {item['modalidade'].capitalize()}\n"
                    linha += f"Dezenas: {', '.join(item['dezenas'])}\n"
                    if item['trevos']:
                        linha += f"Trevos: {', '.join(item['trevos'])}\n"
                    linha += "-"*30 + "\n"
                    f.write(linha)
                    
            mostrar_snack(f"Salvo em: {arquivo_path}")
        except Exception as ex:
            mostrar_snack(f"Erro ao exportar: {str(ex)}")

    btn_gerar = ft.ElevatedButton(
        "🎲 Gerar Combinações",
        color=ft.Colors.WHITE,
        bgcolor=COR_BOTAO_GERAR,
        width=float('inf'),
        height=50,
        on_click=btn_gerar_click
    )
    
    btn_exportar = ft.ElevatedButton(
        "💾 Exportar Resultados",
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_700,
        width=float('inf'),
        height=50,
        on_click=btn_exportar_click
    )

    page.add(
        header,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        dropdown_modalidade,
        dropdown_tamanho,
        txt_dezenas_fixas,
        switch_quentes,
        txt_quantidade,
        btn_gerar,
        btn_exportar,
        ft.Divider(height=20, color=ft.Colors.WHITE24),
        container_resultados
    )

if __name__ == "__main__":
    ft.app(target=main)
