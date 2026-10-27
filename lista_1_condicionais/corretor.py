# =====================================================================
#  CORRETOR AUTOMATICO — Lista 1 (condicionais: if / elif / else)
#  Como usar no notebook/Colab:
#      from corretor import avaliar
#      avaliar(1)   # corrige o Exercicio 1
#      avaliar(2)   # corrige o Exercicio 2
#      avaliar(3)   # corrige o Exercicio 3
#  Este arquivo e baixado pela celula de configuracao da lista.
# =====================================================================
#
#  COMO FUNCIONA (para quem for ler o codigo):
#  - O corretor procura no historico do notebook (_ih) a ultima celula
#    que comeca com o marcador "# EXERCICIO <n>".
#  - Retira dela as linhas que atribuem as variaveis de entrada e
#    re-executa o resto uma vez para cada caso de teste, trocando os
#    valores de entrada e conferindo a variavel de resposta.
#  - Por isso o aluno deve: (1) manter o marcador na primeira linha,
#    (2) nao renomear as variaveis, (3) nao apagar as linhas de
#    entrada (elas comecam com os nomes fixos de cada exercicio).
# =====================================================================

import re

TOLERANCIA = 0.01   # aceita diferencas de arredondamento (centavos)

# ---------------------------------------------------------------------
#  Definicao dos exercicios.
#  entradas: variaveis que o corretor injeta (o aluno NAO define)
#  saida:    variavel que o codigo do aluno deve definir como resposta
#  casos:    lista de (valores de entrada, valor esperado da saida)
# ---------------------------------------------------------------------

EXERCICIOS = {
    1: {
        "rotulo": "Exercicio 1 — aprovacao por nota",
        "marcador": "# EXERCICIO 1",
        "entradas": ["nota"],
        "saida": "categoria",
        "casos": [
            ({"nota": 0},   "reprovado"),
            ({"nota": 15},  "reprovado"),
            ({"nota": 39},  "reprovado"),
            ({"nota": 40},  "aprovado"),    # limite: nota 40 aprova
            ({"nota": 55},  "aprovado"),
            ({"nota": 59},  "aprovado"),
            ({"nota": 60},  "aprovado"),
            ({"nota": 100}, "aprovado"),
        ],
    },
    2: {
        "rotulo": "Exercicio 2 — multa de radar",
        "marcador": "# EXERCICIO 2",
        "entradas": ["velocidade_medida", "velocidade_maxima"],
        "saida": "resultado",
        "casos": [
            ({"velocidade_medida": 30,  "velocidade_maxima": 60}, "ok"),
            ({"velocidade_medida": 60,  "velocidade_maxima": 60}, "ok"),
            ({"velocidade_medida": 65,  "velocidade_maxima": 60}, "leve"),
            ({"velocidade_medida": 66,  "velocidade_maxima": 60}, "leve"),
            ({"velocidade_medida": 67,  "velocidade_maxima": 60}, "grave"),
            ({"velocidade_medida": 90,  "velocidade_maxima": 60}, "grave"),
            ({"velocidade_medida": 91,  "velocidade_maxima": 60}, "gravissima"),
            ({"velocidade_medida": 120, "velocidade_maxima": 60}, "gravissima"),
            ({"velocidade_medida": 88,  "velocidade_maxima": 80}, "leve"),
            ({"velocidade_medida": 100, "velocidade_maxima": 80}, "grave"),
            ({"velocidade_medida": 119, "velocidade_maxima": 80}, "grave"),
            ({"velocidade_medida": 121, "velocidade_maxima": 80}, "gravissima"),
        ],
    },
    3: {
        "rotulo": "Exercicio 3 — custo de hospedagem",
        "marcador": "# EXERCICIO 3",
        "entradas": ["noites", "diaria", "semana"],
        "saida": "custo_total",
        "casos": [
            ({"noites": 2,   "diaria": 300.0, "semana": 2},  600.0),
            ({"noites": 5,   "diaria": 300.0, "semana": 2},  1500.0),
            ({"noites": 6,   "diaria": 300.0, "semana": 2},  1620.0),
            ({"noites": 7,   "diaria": 200.0, "semana": 2},  1260.0),
            ({"noites": 7,   "diaria": 300.0, "semana": 40}, 1890.0),  # semana 40 e par
            ({"noites": 31,  "diaria": 300.0, "semana": 2},  6510.0),
            ({"noites": 70,  "diaria": 100.0, "semana": 2},  4900.0),
            ({"noites": 100, "diaria": 100.0, "semana": 2},  7000.0),
            ({"noites": 12,  "diaria": 10.0,  "semana": 2},  108.0),
            ({"noites": 0,   "diaria": 10.0,  "semana": 2},  0.0),
            ({"noites": 1,   "diaria": 0.0,   "semana": 2},  0.0),
        ],
    },
}

# Desafio do Exercicio 3 (+1 ponto): semana impar e exatamente 7 noites
CASOS_DESAFIO = [
    ({"noites": 7, "diaria": 300.0, "semana": 7},  1795.5),   # 1890.0 - 5%
    ({"noites": 7, "diaria": 300.0, "semana": 12}, 1890.0),   # semana par
    ({"noites": 7, "diaria": 200.0, "semana": 21}, 1197.0),
    ({"noites": 7, "diaria": 100.0, "semana": 33}, 598.5),
    ({"noites": 13, "diaria": 250.0, "semana": 5}, 2925.0),   # nao e "exatamente 7"
]


def checa(resultado, esperado):
    """Compara o resultado do aluno com o valor esperado."""
    if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
        return isinstance(resultado, (int, float)) and abs(resultado - esperado) < TOLERANCIA
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


def rodar_casos(codigo_limpo, casos, saida, rotulo, peso_maximo=0.0):
    """Executa o codigo para cada caso e imprime [OK]/[FALHOU] por caso."""
    ok = 0
    falhas_ellipsis = 0
    for valores, esperado in casos:
        env = {"__name__": "corrigido"}
        env.update(valores)
        try:
            exec(compile(codigo_limpo, rotulo, "exec"), env)
        except Exception as erro:
            print(f"  [FALHOU] {rotulo} {valores!r} -> {type(erro).__name__}: {erro}")
            continue
        resultado = env.get(saida)
        if resultado is ...:
            falhas_ellipsis += 1
            print(f"  [FALHOU] {rotulo} {valores!r} -> ainda ha '...' sem preencher.")
        elif checa(resultado, esperado):
            ok += 1
            print(f"  [OK]     {rotulo} {valores!r} -> {resultado!r}")
        else:
            print(f"  [FALHOU] {rotulo} {valores!r} -> {resultado!r}   (esperado {esperado!r})")
    total = len(casos)
    pontos = ok / total * peso_maximo
    if peso_maximo > 0:
        print(f"  ({rotulo}: {ok}/{total} casos -> {pontos:.1f} pontos)")
    else:
        print(f"  ({rotulo}: {ok}/{total} casos)")
    return ok, total, pontos, falhas_ellipsis


def avaliar(n):
    """Corrige o exercicio n (1, 2 ou 3) lendo a celula do notebook."""
    if n not in EXERCICIOS:
        print(f"AVISO: exercicio desconhecido ({n!r}). Use avaliar(1), avaliar(2) ou avaliar(3).")
        return

    cfg = EXERCICIOS[n]

    # 1) localiza o codigo do aluno no historico do notebook
    try:
        codigo = pega_codigo_aluno(n)
    except NameError:
        print("ERRO: este corretor so funciona dentro do notebook (Jupyter/Colab).")
        return
    if codigo is None:
        print(f"Ainda nao encontrei nenhuma celula com o marcador '{cfg['marcador']}'.")
        print(f"Rode a celula do exercicio {n} antes de corrigir.")
        return

    # 2) retira as linhas de entrada e valida a sintaxe
    codigo_limpo = prepara_codigo(codigo, cfg["entradas"])
    try:
        compile(codigo_limpo, f"<exercicio {n}>", "exec")
    except SyntaxError as e:
        print(f"Erro de SINTAXE na celula do exercicio {n} (linha {e.lineno}): {e.msg}")
        print("Confira dois-pontos no fim de if/elif/else e a indentacao (4 espacos).")
        return

    print("=" * 60)
    print(f"  Corrigindo: {cfg['rotulo']}")
    print("=" * 60)

    if n == 3:
        ok1, n1, p1, f1 = rodar_casos(codigo_limpo, cfg["casos"], cfg["saida"], "[parte 1]", 9.0)
        ok2, n2, p2, f2 = rodar_casos(codigo_limpo, CASOS_DESAFIO, cfg["saida"], "[desafio]", 1.0)
        print("-" * 60)
        print(f"  Nota: {p1 + p2:.1f} / 10   (parte 1: {ok1}/{n1} + desafio: {ok2}/{n2})")
        print("-" * 60)
        if ok1 == n1 and ok2 == n2:
            print("  *** PARABENS! Parte 1 e desafio: tudo certo. ***")
        elif ok1 == n1:
            print("  Parte 1 completa! Falta o desafio (semana impar & 7 noites).")
        elif ok2 == n2:
            print("  Desafio ok! Revise as faixas da parte 1 (limites 5 e 29).")
        else:
            print("  Confira acima os casos que falharam e as faixas da tabela.")
        if f1 + f2 > 0:
            print("  (Ainda ha '...' do modelo sem completar no exercicio 3.)")
        return

    ok, total, _, falhas_ellipsis = rodar_casos(codigo_limpo, cfg["casos"], cfg["saida"], "[ex" + str(n) + "]")
    print("-" * 60)
    nota = ok / total * 10
    print(f"  Nota: {nota:.1f} / 10   ({ok} de {total} casos)")
    print("-" * 60)
    if ok == total:
        print("  *** PARABENS! Todos os casos passaram. ***")
    elif ok == 0 and falhas_ellipsis == total:
        print(f"  Voce ainda nao completou o modelo: substitua cada '...' pela")
        print(f"  condicao/texto certo e rode o corretor de novo.")
    elif ok == 0:
        print("  Nenhum caso passou. Confira: nomes das variaveis-resposta")
        print("  (minusculas, sem acento), strings exatas e os sinais <= / >=.")
    else:
        print("  Quase la! Veja acima os casos que falharam.")