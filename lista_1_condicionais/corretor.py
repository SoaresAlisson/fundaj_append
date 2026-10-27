# =====================================================================
#  CORRETOR AUTOMATICO — Lista 1 (condicionais: if / elif / else)
#  Como usar no notebook/Colab:
#      from corretor import avaliar
#      avaliar(esta_aprovado)            # exercicio 1
#      avaliar(classificar_velocidade)   # exercicio 2
#      avaliar(custo_estadia)            # exercicio 3
#  Este arquivo e baixado pela celula de configuracao do exercicio.
# =====================================================================

TOLERANCIA = 0.01   # aceita diferencas de arredondamento (centavos)

# --- Exercicio 1: aprovacao por nota --------------------------------
# cada caso: (argumentos, esperado)
CASOS_APROVACAO = [
    ((0,),   "reprovado"),
    ((15,),  "reprovado"),
    ((39,),  "reprovado"),
    ((40,),  "aprovado"),   # limite: 40 entra
    ((55,),  "aprovado"),
    ((59,),  "aprovado"),
    ((60,),  "aprovado"),
    ((100,), "aprovado"),
]

# --- Exercicio 2: multa de radar ------------------------------------
# cada caso: ((velocidade_medida, velocidade_maxima), esperado)
CASOS_RADAR = [
    ((30, 60),  "ok"),         # bem abaixo do limite
    ((60, 60),  "ok"),         # exatamente no limite
    ((65, 60),  "leve"),       # ate 10% acima: 61..66 (int(1.1*60)=66)
    ((66, 60),  "leve"),       # limite da faixa leve
    ((67, 60),  "grave"),      # passou de 66, ainda ate 90
    ((90, 60),  "grave"),      # limite da faixa grave (int(1.5*60)=90)
    ((91, 60),  "gravissima"), # passou de 90
    ((120, 60), "gravissima"), # dobro do limite
    ((88, 80),  "leve"),       # outro radar: int(1.1*80)=88
    ((100, 80), "grave"),      # 100 > 88, ainda <= int(1.5*80)=120
    ((119, 80), "grave"),
    ((121, 80), "gravissima"),
]

# --- Exercicio 3: custo de hospedagem --------------------------------
# cada caso: ((numero_diarias, preco_diaria, numero_semana), esperado)
CASOS_HOSPEDAGEM = [
    ((2, 300.0, 2),   600.0),     # curta:   2 x 300 (sem desconto)
    ((5, 300.0, 2),   1500.0),    # curta:   5 x 300
    ((6, 300.0, 2),   1620.0),    # 6..29:   6 x 270 (10% off)
    ((7, 200.0, 2),   1260.0),    # 7 x 180
    ((7, 300.0, 2),   1890.0),    # 7 x 270 (semana par: sem extra)
    ((31, 300.0, 2),  6510.0),    # >=30:    31 x 210 (30% off)
    ((70, 100.0, 2),  4900.0),    # >=30:    70 x 70
    ((71, 100.0, 2),  4970.0),    # >=30:    71 x 70
    ((100, 100.0, 2), 7000.0),    # >=30:    100 x 70
    ((12, 10.0, 2),   108.0),     # valores pequenos
    ((0, 300.0, 2),   0.0),       # zero diarias -> 0.0
    ((5, 0.0, 2),     0.0),       # diaria zero  -> 0.0
]

# DESAFIO (semana impar + exatamente 7 diarias -> +5% de desconto)
CASOS_DESAFIO = [
    ((7, 300.0, 7),  1795.5),     # 1890.0 - 5%
    ((7, 300.0, 12), 1890.0),     # semana par: sem extra
    ((7, 200.0, 21), 1197.0),     # 1260.0 - 5%
    ((7, 100.0, 33), 598.5),      # 630.0  - 5%
    ((13, 250.0, 5), 2925.0),     # 13 diarias: nao e "exatamente 7"
]

ROTULOS = {
    "esta_aprovado":          "Exercicio 1 — aprovacao por nota",
    "classificar_velocidade": "Exercicio 2 — multa de radar",
    "custo_estadia":          "Exercicio 3 — custo de hospedagem",
}


def checa(resultado, esperado):
    if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
        return isinstance(resultado, (int, float)) and abs(resultado - esperado) < TOLERANCIA
    return resultado == esperado


def rodar_casos(fn, casos, rotulo, peso_maximo=0.0):
    ok = 0
    for entrada, esperado in casos:
        nome_caso = f"{fn.__name__}({', '.join(repr(a) for a in entrada)})"
        try:
            resultado = fn(*entrada)
        except Exception as erro:
            print(f"  [FALHOU] {rotulo} {nome_caso} -> {type(erro).__name__}: {erro}")
            continue
        if resultado is ...:
            print(f"  [FALHOU] {rotulo} {nome_caso} -> ficou o '...' do modelo; complete a funcao.")
        elif checa(resultado, esperado):
            ok += 1
            print(f"  [OK]     {rotulo} {nome_caso} -> {resultado!r}")
        else:
            print(
                f"  [FALHOU] {rotulo} {nome_caso} -> {resultado!r}"
                f"   (esperado {esperado!r})"
            )
    pontos = ok / len(casos) * peso_maximo
    resumo = f"({rotulo}: {ok}/{len(casos)} casos"
    if peso_maximo > 0:
        resumo += f" -> {pontos:.1f} pontos"
    print(f"  {resumo})")
    return ok, len(casos), pontos, rotulo


def avaliar(fn):
    if not callable(fn):
        print("AVISO: passe a FUNCAO em si, sem aspas e sem parenteses.")
        print("  Certo:   avaliar(esta_aprovado)")
        print("  Errado:  avaliar('esta_aprovado')  |  avaliar(esta_aprovado())")
        print(f"  Voce passou: {fn!r}")
        return
    nome = getattr(fn, "__name__", "")
    if nome not in ROTULOS:
        print(f"AVISO: funcao desconhecida: {fn!r}")
        print("O corretor conhece:")
        for n, r in ROTULOS.items():
            print(f"  avaliar({n})   # {r}")
        return

    print("=" * 60)
    print(f"  Corrigindo: {ROTULOS[nome]}")
    print("=" * 60)
    if nome == "esta_aprovado":
        ok, n, _, _ = rodar_casos(fn, CASOS_APROVACAO, "[ex1]")
        total_casos, total_ok = n, ok

    elif nome == "classificar_velocidade":
        ok, n, _, _ = rodar_casos(fn, CASOS_RADAR, "[ex2]")
        total_casos, total_ok = n, ok

    else:  # custo_estadia
        ok1, n1, p1, _ = rodar_casos(fn, CASOS_HOSPEDAGEM, "[parte 1]", 9.0)
        ok2, n2, p2, _ = rodar_casos(fn, CASOS_DESAFIO, "[desafio]", 1.0)
        print("-" * 60)
        print(f"  Nota: {p1 + p2:.1f} / 10   (parte 1: {ok1}/{n1} + desafio: {ok2}/{n2})")
        print("-" * 60)
        if ok1 == n1 and ok2 == n2:
            print("  *** PARABENS! Parte 1 e desafio: tudo certo. ***")
        elif ok1 == n1:
            print("  Parte 1 completa! Falta o desafio (semana impar & 7 diarias).")
        elif ok2 == n2:
            print("  Desafio ok! Revise as faixas da parte 1 (limites 5 e 29).")
        else:
            print("  Confira acima os casos que falharam e as faixas da tabela.")
        return

    print("-" * 60)
    nota = total_ok / total_casos * 10
    print(f"  Nota: {nota:.1f} / 10   ({total_ok} de {total_casos} casos)")
    print("-" * 60)
    if total_ok == total_casos:
        print("  *** PARABENS! Todos os casos passaram. ***")
    elif total_ok == 0:
        print("  Nenhum caso passou. Confira: nome da funcao, strings exatas")
        print("  (minusculas, sem acento) e os sinais <= / >=.")
    else:
        print("  Quase la! Veja acima os casos que falharam.")