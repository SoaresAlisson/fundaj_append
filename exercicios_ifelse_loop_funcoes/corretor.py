# =====================================================================
#  CORRETOR AUTOMATICO — Exercicios: if / elif / else / and / or,
#  lacos for e funcoes (def / return)
#  Como usar no notebook/Colab:
#      from corretor import avaliar, verificar_preenchimento_questoes
#      avaliar(1)  ... avaliar(7)   # corrige o exercicio n
#      verificar_preenchimento_questoes()   # confere se tudo foi feito + nome
#  Este arquivo e baixado pela celula de configuracao do notebook.
# =====================================================================
#
#  COMO FUNCIONA (para quem for ler o codigo):
#  - Nos exercicios 1 a 6 o corretor procura no historico do notebook
#    (_ih) a ultima celula que comeca com o marcador "# EXERCICIO <n>",
#    retira dela as linhas que atribuem as variaveis de entrada e
#    re-executa o resto uma vez para cada caso de teste, trocando os
#    valores de entrada e conferindo a variavel de resposta.
#  - No exercicio 7 (funcao) ele executa a celula uma unica vez para
#    definir a funcao gorjeta() e depois CHAMA a funcao em cada caso
#    de teste, conferindo o valor devolvido pelo return.
#  - Por isso o aluno deve: (1) manter o marcador na primeira linha,
#    (2) nao renomear as variaveis (nem a funcao gorjeta), (3) nao
#    apagar as linhas de entrada (elas comecam com os nomes fixos de
#    cada exercicio).
# =====================================================================

import copy
import re

TOLERANCIA = 0.01  # aceita diferencas de arredondamento (centavos)

# ---------------------------------------------------------------------
#  Definicao dos exercicios.
#  entradas: variaveis que o corretor injeta (o aluno NAO define)
#  saida:    variavel que o codigo do aluno deve definir como resposta
#  casos:    exercicios 1-6 -> [(valores de entrada, valor esperado)]
#            exercicio 7    -> [(argumentos da chamada, valor esperado)]
# ---------------------------------------------------------------------

EXERCICIOS = {
    1: {
        "rotulo": "Exercicio 1 — aprovacao por nota",
        "marcador": "# EXERCICIO 1",
        "entradas": ["nota"],
        "saida": "categoria",
        "casos": [
            ({"nota": 0}, "reprovado"),
            ({"nota": 15}, "reprovado"),
            ({"nota": 39}, "reprovado"),
            ({"nota": 40}, "aprovado"),  # limite: nota 40 aprova
            ({"nota": 55}, "aprovado"),
            ({"nota": 59}, "aprovado"),
            ({"nota": 60}, "aprovado"),
            ({"nota": 100}, "aprovado"),
        ],
    },
    2: {
        "rotulo": "Exercicio 2 — multa de radar",
        "marcador": "# EXERCICIO 2",
        "entradas": ["velocidade_medida", "velocidade_maxima"],
        "saida": "resultado",
        "casos": [
            ({"velocidade_medida": 30, "velocidade_maxima": 60}, "ok"),
            ({"velocidade_medida": 60, "velocidade_maxima": 60}, "ok"),
            ({"velocidade_medida": 65, "velocidade_maxima": 60}, "leve"),
            ({"velocidade_medida": 66, "velocidade_maxima": 60}, "leve"),
            ({"velocidade_medida": 67, "velocidade_maxima": 60}, "grave"),
            ({"velocidade_medida": 90, "velocidade_maxima": 60}, "grave"),
            ({"velocidade_medida": 91, "velocidade_maxima": 60}, "gravissima"),
            ({"velocidade_medida": 120, "velocidade_maxima": 60}, "gravissima"),
            ({"velocidade_medida": 88, "velocidade_maxima": 80}, "leve"),
            ({"velocidade_medida": 100, "velocidade_maxima": 80}, "grave"),
            ({"velocidade_medida": 119, "velocidade_maxima": 80}, "grave"),
            ({"velocidade_medida": 121, "velocidade_maxima": 80}, "gravissima"),
        ],
    },
    3: {
        "rotulo": "Exercicio 3 — auxilio da prefeitura (and)",
        "marcador": "# EXERCICIO 3",
        "entradas": ["renda", "moradores"],
        "saida": "categoria",
        "casos": [
            ({"renda": 2500.0, "moradores": 5}, "elegivel"),
            ({"renda": 1000.0, "moradores": 4}, "elegivel"),    # borda: 4 moradores conta
            ({"renda": 2999.99, "moradores": 4}, "elegivel"),   # renda 1 centavo abaixo do corte
            ({"renda": 2500.0, "moradores": 4}, "elegivel"),    # as duas bordas juntas
            ({"renda": 1500.0, "moradores": 8}, "elegivel"),
            ({"renda": 2500.0, "moradores": 3}, "nao_elegivel"),  # moradores 3
            ({"renda": 3000.0, "moradores": 5}, "nao_elegivel"),  # 3000 nao e menor que 3000
            ({"renda": 3500.0, "moradores": 4}, "nao_elegivel"),
            ({"renda": 3000.0, "moradores": 3}, "nao_elegivel"),  # as duas falham
            ({"renda": 5000.0, "moradores": 2}, "nao_elegivel"),
        ],
    },
    4: {
        "rotulo": "Exercicio 4 — loja abre no fim de semana (or)",
        "marcador": "# EXERCICIO 4",
        "entradas": ["dia"],
        "saida": "abre",
        "casos": [
            ({"dia": "sabado"}, True),
            ({"dia": "domingo"}, True),
            ({"dia": "segunda"}, False),
            ({"dia": "terca"}, False),
            ({"dia": "quarta"}, False),
            ({"dia": "quinta"}, False),
            ({"dia": "sexta"}, False),
        ],
    },
    5: {
        "rotulo": "Exercicio 5 — total da barraca na feira",
        "marcador": "# EXERCICIO 5",
        "entradas": ["ganhos"],
        "saida": "total",
        "casos": [
            ({"ganhos": [120.50, 89.90, 45.00, 210.00, 33.75]}, 499.15),  # a lista do modelo
            ({"ganhos": []}, 0.0),                    # lista vazia: total fica 0.0
            ({"ganhos": [250.00]}, 250.0),            # um unico dia
            ({"ganhos": [10, 20, 30]}, 60.0),         # inteiros tambem somam
            ({"ganhos": [1.5, 2.25, 0.25]}, 4.0),     # floats
            ({"ganhos": [-50.0, 50.0, 20.0]}, 20.0),  # prejuizo compensa
            ({"ganhos": [0.0, 0.0, 0.0]}, 0.0),       # dias zerados
        ],
    },
    6: {
        "rotulo": "Exercicio 6 — dias de chuva forte",
        "marcador": "# EXERCICIO 6",
        "entradas": ["chuvas", "limite"],
        "saida": "dias_fortes",
        "casos": [
            ({"chuvas": [12.0, 63.5, 50.0, 8.0, 91.2, 49.9, 75.0], "limite": 50.0}, 4),  # o modelo
            ({"chuvas": [], "limite": 50.0}, 0),                # sem dados
            ({"chuvas": [40.0, 49.9, 30.0], "limite": 50.0}, 0),  # nenhum dia forte
            ({"chuvas": [50.0], "limite": 50.0}, 1),            # borda: igual ao limite conta
            ({"chuvas": [49.9], "limite": 50.0}, 0),            # borda: 0.1 a menos nao conta
            ({"chuvas": [80.0, 90.0, 70.0], "limite": 50.0}, 3),  # todos os dias
            ({"chuvas": [10.0, 20.0, 30.0], "limite": 25.0}, 1),  # limite no meio da lista
            ({"chuvas": [5.0, 0.0, 12.5], "limite": 0.0}, 3),   # limite zero: 0.0 tambem conta
        ],
    },
    7: {
        "rotulo": "Exercicio 7 — gorjeta do restaurante",
        "marcador": "# EXERCICIO 7",
        "entradas": [],
        "funcao": "gorjeta",
        "casos": [
            ((150.0,), 15.0),        # percentual padrao (10)
            ((200.0, 15), 30.0),     # percentual explicito
            ((80.0, 0), 0.0),        # sem gorjeta
            ((123.45,), 12.345),     # float com tolerancia 0.01
            ((100.0, 12.5), 12.5),   # percentual decimal
            ((1000.0, 5), 50.0),     # conta grande
            ((0.0,), 0.0),           # conta zerada
        ],
    },
}


def checa(resultado, esperado):
    """Compara o resultado do aluno com o valor esperado."""
    if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
        return (
            isinstance(resultado, (int, float))
            and abs(resultado - esperado) < TOLERANCIA
        )
    return resultado == esperado


def prepara_codigo(codigo, entradas):
    """Retira do codigo do aluno as linhas que definem as variaveis de entrada."""
    padrao = re.compile(
        r"^\s*(?:" + "|".join(re.escape(e) for e in entradas) + r")\s*=.*$"
    )
    linhas_boas = [l for l in codigo.splitlines() if not padrao.match(l)]
    return "\n".join(linhas_boas)


def pega_codigo_aluno(n):
    """Encontra no historico do notebook a ultima celula do exercicio n."""
    ip = get_ipython()
    marcador = "# EXERCICIO " + str(n)
    for celula in reversed(ip.history_manager.input_hist_parsed):
        primeira_linha = celula.split("\n", 1)[0].strip()
        if primeira_linha == marcador:
            return celula
    return None


def tem_pontinhos(codigo_limpo):
    """True se ainda ha '...' no codigo do aluno (ignorando comentarios).

    Em lacos, um modelo com '...' nem compila (ex.: 'for ...:'); por isso
    o corretor checa isto ANTES da sintaxe e avisa de forma amigavel.
    """
    for linha in codigo_limpo.splitlines():
        trecho = re.sub(r"#.*$", "", linha)  # ignora comentario no fim da linha
        if "..." in trecho:
            return True
    return False


def rodar_casos(codigo_limpo, casos, saida, rotulo, peso_maximo=0.0, imprimir=True):
    """Exercicios 1 a 6: executa o codigo para cada caso de teste."""
    ok = 0
    for valores, esperado in casos:
        env = {"__name__": "corrigido"}
        env.update(copy.deepcopy(valores))  # copia: aluno nao pode poluir os casos
        try:
            exec(compile(codigo_limpo, rotulo, "exec"), env)
        except Exception as erro:
            if imprimir:
                print(
                    f"  [FALHOU] {rotulo} {valores!r} -> {type(erro).__name__}: {erro}"
                )
            continue
        resultado = env.get(saida)
        if resultado is None:
            if imprimir:
                print(
                    f"  [FALHOU] {rotulo} {valores!r} -> a variavel {saida} nao"
                    " ficou definida no seu codigo"
                )
            continue
        if checa(resultado, esperado):
            ok += 1
            if imprimir:
                print(f"  [OK]     {rotulo} {valores!r} -> {resultado!r}")
        elif imprimir:
            print(
                f"  [FALHOU] {rotulo} {valores!r} -> {resultado!r}"
                f"   (esperado {esperado!r})"
            )
    total = len(casos)
    pontos = ok / total * peso_maximo
    if imprimir:
        if peso_maximo > 0:
            print(f"  ({rotulo}: {ok}/{total} casos -> {pontos:.1f} pontos)")
        else:
            print(f"  ({rotulo}: {ok}/{total} casos)")
    return ok, total, pontos


def _chamada(nome_funcao, argumentos):
    """Formata 'gorjeta(150.0, 15)' para as mensagens do corretor."""
    dentro = ", ".join(repr(a) for a in argumentos)
    return f"{nome_funcao}({dentro})"


def rodar_casos_funcao(codigo_limpo, nome_funcao, casos, rotulo, peso_maximo=10.0, imprimir=True):
    """Exercicio 7: define a funcao do aluno e a chama para cada caso."""
    env = {"__name__": "corrigido"}
    try:
        exec(compile(codigo_limpo, rotulo, "exec"), env)
    except Exception as erro:
        if imprimir:
            print(
                f"  [FALHOU] {type(erro).__name__} ao executar a sua celula: {erro}"
            )
        return 0, len(casos), 0.0

    funcao = env.get(nome_funcao)
    if funcao is None or not callable(funcao):
        if imprimir:
            print(f"  [FALHOU] Nao encontrei a funcao {nome_funcao}() na sua celula.")
            print("  Confira o nome na linha 'def' e rode a celula de novo.")
        return 0, len(casos), 0.0

    ok = 0
    for argumentos, esperado in casos:
        chamada = _chamada(nome_funcao, argumentos)
        try:
            resultado = funcao(*argumentos)
        except TypeError as erro:
            if imprimir:
                print(f"  [FALHOU] {chamada} -> TypeError: {erro}")
                if "argument" in str(erro):
                    print("           Confira a linha 'def': o percentual precisa de")
                    print("           valor padrao (percentual=10).")
            continue
        except Exception as erro:
            if imprimir:
                print(
                    f"  [FALHOU] {chamada} -> {type(erro).__name__}: {erro}"
                )
            continue
        if resultado is None:
            if imprimir:
                print(f"  [FALHOU] {chamada} -> devolveu None")
                print("           Use 'return' para devolver o valor (sem 'print').")
            continue
        if checa(resultado, esperado):
            ok += 1
            if imprimir:
                print(f"  [OK]     {chamada} -> {resultado!r}")
        elif imprimir:
            print(f"  [FALHOU] {chamada} -> {resultado!r}   (esperado {esperado!r})")
    total = len(casos)
    pontos = ok / total * peso_maximo
    if imprimir:
        print(f"  ({rotulo}: {ok}/{total} casos -> {pontos:.1f} pontos)")
    return ok, total, pontos


def avaliar(n, imprimir=True):
    """Corrige o exercicio n (1 a 7) lendo a celula do notebook.

    Devolve (ok, total, pontos) para uso do
    verificar_preenchimento_questoes(); imprimir=False suprime a
    saida detalhada.
    """
    if n not in EXERCICIOS:
        print(
            f"AVISO: exercicio desconhecido ({n!r}). Use avaliar(1) ate avaliar(7)."
        )
        return None

    cfg = EXERCICIOS[n]

    # 1) localiza o codigo do aluno no historico do notebook
    try:
        codigo = pega_codigo_aluno(n)
    except NameError:
        if imprimir:
            print("ERRO: este corretor so funciona dentro do notebook (Jupyter/Colab).")
        return None
    if codigo is None:
        if imprimir:
            print(
                f"Ainda nao encontrei nenhuma celula com o marcador '{cfg['marcador']}'."
            )
            print(f"Rode a celula do exercicio {n} antes de corrigir.")
        return None

    # 2) retira as linhas de entrada (exercicio 7 nao tem variaveis de entrada)
    if cfg["entradas"]:
        codigo_limpo = prepara_codigo(codigo, cfg["entradas"])
    else:
        codigo_limpo = codigo

    # 3) modelo ainda com '...'? avisa antes de qualquer coisa
    if tem_pontinhos(codigo_limpo):
        if imprimir:
            print("=" * 60)
            print(f"  Corrigindo: {cfg['rotulo']}")
            print("=" * 60)
            print("  Voce ainda nao completou o modelo: substitua cada '...' pelo")
            print("  que falta, rode a celula e chame o corretor de novo.")
        return (0, len(cfg["casos"]), 0.0)

    # 4) valida a sintaxe
    try:
        compile(codigo_limpo, f"<exercicio {n}>", "exec")
    except SyntaxError as e:
        if imprimir:
            print(
                f"Erro de SINTAXE na celula do exercicio {n} (linha {e.lineno}): {e.msg}"
            )
            print("Confira os dois-pontos no fim de for/if e a indentacao (4 espacos).")
        return None

    if imprimir:
        print("=" * 60)
        print(f"  Corrigindo: {cfg['rotulo']}")
        print("=" * 60)

    # 5) o exercicio 5 pede o laco 'for': recusa sum()
    if n == 5 and re.search(r"\bsum\s*\(", codigo_limpo):
        if imprimir:
            print("  [FALHOU] O enunciado pede um laco 'for' para somar: nao use sum().")
            print("  Refaca com o laco, rode a celula e chame o corretor de novo.")
        return (0, len(cfg["casos"]), 0.0)

    # 6) roda os casos de teste
    if n == 7:
        ok, total, pontos = rodar_casos_funcao(
            codigo_limpo, cfg["funcao"], cfg["casos"], "[ex7]", 10.0, imprimir
        )
    else:
        ok, total, pontos = rodar_casos(
            codigo_limpo, cfg["casos"], cfg["saida"], "[ex" + str(n) + "]", 10.0, imprimir
        )

    if imprimir:
        print("-" * 60)
        print(f"  Nota: {pontos:.1f} / 10   ({ok} de {total} casos)")
        print("-" * 60)
        if ok == total:
            print("  *** PARABENS! Todos os casos passaram. ***")
        elif ok == 0:
            print("  Nenhum caso passou. Leia as mensagens [FALHOU] acima com calma.")
            if n == 7:
                print("  Confira o 'return' da funcao e o calculo da gorjeta.")
            else:
                print("  Confira o nome da variavel-resposta, as strings exatas")
                print("  pedidas na tabela e os sinais <= / >=.")
        else:
            print("  Quase la! Veja acima os casos que falharam.")
    return (ok, total, pontos)


# ---------------------------------------------------------------------
#  TESTE DOS TESTES — verificacao final da entrega
# ---------------------------------------------------------------------


def verificar_preenchimento_questoes(imprimir=True):
    """Confere se todos os exercícios estão completos e o nome foi preenchido.

    Retorna (lista_ok, nome):
      lista_ok : True se os 7 exercicios passaram em todos os casos
      nome     : string lida da celula de identificacao (ou None)
    """
    ip = get_ipython()
    historico = ip.history_manager.input_hist_parsed

    # --- exercicios: refaz a correcao de cada um, silenciosa ------------
    exercicios_ok = True
    resumo = []
    for n in sorted(EXERCICIOS):
        resultado = avaliar(n, imprimir=False)
        if resultado is None:
            exercicios_ok = False
            resumo.append((n, None))
        else:
            ok, total, pontos = resultado
            completo = ok == total
            exercicios_ok = exercicios_ok and completo
            resumo.append((n, completo))

    # --- nome: procura a ultima celula com o marcador de identificacao --
    nome = None
    for celula in reversed(historico):
        primeira = celula.split("\n", 1)[0].strip()
        if primeira != "# MEU NOME":
            continue
        # extrai o valor da atribuicao meu_nome = "..." (ou '...')
        m = re.search(r'^\s*meu_nome\s*=\s*["\'](.+?)["\']\s*(?:#.*)?$', celula, re.M)
        if m and m.group(1).strip() and set(m.group(1).strip()) != {"."}:
            nome = m.group(1).strip()
            break

    if imprimir:
        print("=" * 60)
        print("  VERIFICACAO FINAL DA ENTREGA — Exercicios 1 a 7")
        print("=" * 60)
        for n, completo in resumo:
            if completo is None:
                print(
                    f"  Exercicio {n}: PENDENTE  (celula nao rodada ou nao encontrada)"
                )
            elif completo:
                print(f"  Exercicio {n}: COMPLETO (todos os casos passaram)")
            else:
                print(f"  Exercicio {n}: INCOMPLETO (veja 'avaliar({n})' acima)")
        if nome:
            print(f"  Aluno: {nome}")
        else:
            print("  Nome: NAO PREENCHIDO (rode a celula 'Seu nome' no final)")
        print("-" * 60)
        if exercicios_ok and nome:
            print(f"  *** TUDO CERTO, {nome}! Lista pronta para entregar. ***")
        elif exercicios_ok:
            print("  Exercicios completos, mas falta preencher o seu nome.")
        elif nome:
            print("  Nome ok, mas ha exercicio(s) incompleto(s).")
        else:
            print("  Faltam exercicios E o nome.")

    return exercicios_ok, nome