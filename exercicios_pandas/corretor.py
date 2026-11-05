# =====================================================================
#  CORRETOR AUTOMATICO — Exercicios de Pandas (Series, DataFrame,
#  filtragem, value_counts, query, groupby)
#  Como usar no notebook/Colab:
#      from corretor import avaliar, verificar_preenchimento_questoes
#      avaliar(1) ... avaliar(10)    # corrige o exercicio n
#      verificar_preenchimento_questoes()   # confere se tudo foi feito + nome
#  Este arquivo e baixado pela celula de configuracao do notebook.
# =====================================================================
#
#  COMO FUNCIONA (para quem for ler o codigo):
#  - O corretor procura no historico do notebook (_ih) a ultima celula
#    que comeca com o marcador "# EXERCICIO <n>".
#  - Re-executa a celula do aluno e roda uma lista de CHECAGENS sobre
#    a variavel-resposta (definida em cada exercicio). Cada checagem
#    vale a mesma fracao dos 10 pontos.
#  - Nos exercicios 3 a 10 o corretor injeta no ambiente a variavel
#    "df_poprua" (lida do arquivo poprua_cadunico_BH.csv, o mesmo que
#    o aluno baixa no Exercicio 2) e confere o resultado SEMANTICAMENTE
#    contra esse DataFrame — os valores esperados sao derivados dos
#    dados reais, nao fixos no codigo.
#  - Exercicios com metodo exigido (query, groupby, agg) recusam
#    solucoes equivalentes que nao usam o metodo pedido no enunciado.
# =====================================================================

import re

import pandas as pd

TOLERANCIA = 0.01  # aceita diferencas de arredondamento
ARQUIVO_CSV = "poprua_cadunico_BH.csv"

_df_cache = None


def _carregar_df(imprimir=True):
    """Le o CSV da base poprua (o mesmo arquivo que o aluno baixa no ex. 2)."""
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    try:
        _df_cache = pd.read_csv(ARQUIVO_CSV)
        return _df_cache
    except FileNotFoundError:
        if imprimir:
            print(
                f"  [FALHOU] Nao encontrei o arquivo '{ARQUIVO_CSV}' no diretorio"
                " do notebook."
            )
            print("           Rode antes a celula de download (!wget) do Exercicio 2.")
        return None
    except Exception as erro:
        if imprimir:
            print(f"  [FALHOU] Nao consegui ler '{ARQUIVO_CSV}': {erro}")
        return None


# ---------------------------------------------------------------------
#  Historico do notebook
# ---------------------------------------------------------------------


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
    """True se ainda ha '...' no codigo do aluno (ignorando comentarios)."""
    for linha in codigo_limpo.splitlines():
        trecho = re.sub(r"#.*$", "", linha)  # ignora comentario no fim da linha
        if "..." in trecho:
            return True
    return False


# ---------------------------------------------------------------------
#  Comparadores tolerantes
# ---------------------------------------------------------------------


def _strs(x):
    try:
        return list(map(str, x))
    except TypeError:
        return None


def series_perto(obtido, esperado, tol=TOLERANCIA):
    """Compara duas Series numericas por indice, com tolerancia."""
    try:
        if len(obtido) != len(esperado):
            return False
        o = obtido.sort_index()
        e = esperado.sort_index()
        return all(abs(float(a) - float(b)) < tol for a, b in zip(o.values, e.values))
    except Exception:
        return False


def df_agg_perto(obtido, esperado):
    """Compara DataFrame do agg: colunas como conjunto; valores por celula."""
    try:
        if set(_strs(obtido.columns)) != set(_strs(esperado.columns)):
            return False
        if set(_strs(obtido.index)) != set(_strs(esperado.index)):
            return False
        for col in _strs(esperado.columns):
            for idx in _strs(esperado.index):
                a = obtido.loc[idx, col]
                b = esperado.loc[idx, col]
                if col in ("mean", "median"):
                    if abs(float(a) - float(b)) >= TOLERANCIA:
                        return False
                else:
                    if int(a) != int(b):
                        return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
#  Checagens por exercicio: (descricao, funcao(env, df) -> bool)
# ---------------------------------------------------------------------


def _c1_e_series(env, df):
    return isinstance(env.get("precos_desconto"), pd.Series)


def _c1_tamanho(env, df):
    r = env.get("precos_desconto")
    p = env.get("precos")
    return (
        isinstance(r, pd.Series)
        and isinstance(p, (list, tuple))
        and len(p) == 5
        and len(r) == 5
    )


def _c1_valores(env, df):
    r = env.get("precos_desconto")
    p = env.get("precos")
    if not isinstance(r, pd.Series) or not isinstance(p, (list, tuple)):
        return False
    esperado = pd.Series(p) * 0.90
    return series_perto(r.reset_index(drop=True), esperado.reset_index(drop=True))


def _c2_e_df(env, df):
    return isinstance(env.get("df_poprua"), pd.DataFrame)


def _c2_completo(env, df):
    r = env.get("df_poprua")
    return isinstance(r, pd.DataFrame) and r.shape == df.shape


def _c2_colunas(env, df):
    r = env.get("df_poprua")
    if not isinstance(r, pd.DataFrame):
        return False
    nomes = _strs(r.columns)
    return all(c in nomes for c in ("GRAU_INSTRUCAO", "IDADE", "SEXO"))


def _c3_colunas(env, df):
    r = env.get("colunas")
    if r is None:
        return False
    try:
        return _strs(r) == _strs(df.columns)
    except TypeError:
        return False


def _c4_coluna_certa(env, df):
    r = env.get("escolaridade")
    return isinstance(r, pd.Series) and str(r.name) == "GRAU_INSTRUCAO"


def _c4_igual(env, df):
    r = env.get("escolaridade")
    if not isinstance(r, pd.Series):
        return False
    return r.reset_index(drop=True).equals(df["GRAU_INSTRUCAO"].reset_index(drop=True))


def _c5_unicos(env, df):
    r = env.get("unicos")
    if r is None:
        return False
    try:
        return set(_strs(r)) == set(_strs(df["GRAU_INSTRUCAO"].unique()))
    except TypeError:
        return False


def _c5_sem_repeticao(env, df):
    r = env.get("unicos")
    if r is None:
        return False
    try:
        valores = _strs(r)
        return len(valores) == len(set(valores)) and len(valores) == 7
    except TypeError:
        return False


def _c6_e_df(env, df):
    return isinstance(env.get("df_poprua_60mais"), pd.DataFrame)


def _c6_tamanho(env, df):
    r = env.get("df_poprua_60mais")
    if not isinstance(r, pd.DataFrame):
        return False
    return r.shape == df[df["IDADE"] > 60].shape


def _c6_igual(env, df):
    r = env.get("df_poprua_60mais")
    if not isinstance(r, pd.DataFrame):
        return False
    esperado = df[df["IDADE"] > 60]
    return r.reset_index(drop=True).equals(esperado.reset_index(drop=True))


def _c7_contagem(env, df):
    r = env.get("contagem")
    if not isinstance(r, pd.Series):
        return False
    esperado = df["GRAU_INSTRUCAO"].value_counts().sort_index()
    obtido = r.sort_index()
    if _strs(obtido.index) != _strs(esperado.index):
        return False
    return all(int(a) == int(b) for a, b in zip(obtido.values, esperado.values))


def _c8_e_df(env, df):
    return isinstance(env.get("df_filtro"), pd.DataFrame)


def _c8_igual(env, df):
    r = env.get("df_filtro")
    if not isinstance(r, pd.DataFrame):
        return False
    esperado = df.query('IDADE > 60 and SEXO == "FEMININO"')
    return r.reset_index(drop=True).equals(esperado.reset_index(drop=True))


def _c9_media(env, df):
    r = env.get("idade_media_cor")
    if not isinstance(r, pd.Series):
        return False
    return series_perto(r, df.groupby("COR_RACA")["IDADE"].mean())


def _c9_grupos(env, df):
    r = env.get("idade_media_cor")
    if not isinstance(r, pd.Series):
        return False
    return set(_strs(r.index)) == set(_strs(df["COR_RACA"].dropna().unique()))


def _c10_colunas(env, df):
    r = env.get("estatisticas")
    if not isinstance(r, pd.DataFrame):
        return False
    return set(_strs(r.columns)) == {"mean", "median", "count", "min", "max"}


def _c10_valores(env, df):
    r = env.get("estatisticas")
    if not isinstance(r, pd.DataFrame):
        return False
    esperado = df.groupby("COR_RACA")["IDADE"].agg(
        ["mean", "median", "count", "min", "max"]
    )
    return df_agg_perto(r, esperado)


# ---------------------------------------------------------------------
#  Definicao dos exercicios.
#  saida:      variavel que o codigo do aluno deve definir como resposta
#  precisa_df: True -> o corretor injeta df_poprua (lido do CSV local)
#  requer:     [(regex, mensagem)] — metodo exigido pelo enunciado
#  checagens:  [(descricao, funcao)] — cada uma vale 10/len(checagens)
# ---------------------------------------------------------------------

EXERCICIOS = {
    1: {
        "rotulo": "Exercicio 1 — Series com desconto",
        "saida": "precos_desconto",
        "precisa_df": False,
        "requer": [],
        "checagens": [
            ("a resposta e uma pd.Series", _c1_e_series),
            ("a Series tem os 5 precos", _c1_tamanho),
            ("os valores tem 10% de desconto", _c1_valores),
        ],
    },
    2: {
        "rotulo": "Exercicio 2 — importar a base poprua",
        "saida": "df_poprua",
        "precisa_df": True,   # usa o df do corretor so como referencia
        "requer": [],
        "checagens": [
            ("df_poprua e um DataFrame", _c2_e_df),
            ("o arquivo foi lido por completo (todas as linhas e colunas)", _c2_completo),
            ("as colunas esperadas estao presentes", _c2_colunas),
        ],
    },
    3: {
        "rotulo": "Exercicio 3 — nomes das colunas",
        "saida": "colunas",
        "precisa_df": True,
        "requer": [],
        "checagens": [
            ("colunas traz os nomes das colunas do df_poprua", _c3_colunas),
        ],
    },
    4: {
        "rotulo": "Exercicio 4 — coluna de escolaridade",
        "saida": "escolaridade",
        "precisa_df": True,
        "requer": [],
        "checagens": [
            ("selecionou a coluna GRAU_INSTRUCAO", _c4_coluna_certa),
            ("a Series inteira confere com a coluna da base", _c4_igual),
        ],
    },
    5: {
        "rotulo": "Exercicio 5 — valores unicos de GRAU_INSTRUCAO",
        "saida": "unicos",
        "precisa_df": True,
        "requer": [],
        "checagens": [
            ("unicos traz os valores unicos de GRAU_INSTRUCAO", _c5_unicos),
            ("sao 7 valores, sem repeticao", _c5_sem_repeticao),
        ],
    },
    6: {
        "rotulo": "Exercicio 6 — filtrar idade maior que 60",
        "saida": "df_poprua_60mais",
        "precisa_df": True,
        "requer": [],
        "checagens": [
            ("df_poprua_60mais e um DataFrame", _c6_e_df),
            ("so entraram as linhas com mais de 60 anos", _c6_tamanho),
            ("o conteudo confere com o filtro da base", _c6_igual),
        ],
    },
    7: {
        "rotulo": "Exercicio 7 — frequencias por grau de instrucao",
        "saida": "contagem",
        "precisa_df": True,
        "requer": [],
        "checagens": [
            ("contagem traz o value_counts de GRAU_INSTRUCAO", _c7_contagem),
        ],
    },
    8: {
        "rotulo": "Exercicio 8 — query com duas condicoes",
        "saida": "df_filtro",
        "precisa_df": True,
        "requer": [
            (
                r"\.query\s*\(",
                "O enunciado pede o metodo df.query com duas condicoes e 'and'.",
            ),
        ],
        "checagens": [
            ("df_filtro e um DataFrame", _c8_e_df),
            ("so entraram mulheres com mais de 60 anos (IDADE > 60 and SEXO == 'FEMININO')", _c8_igual),
        ],
    },
    9: {
        "rotulo": "Exercicio 9 — idade media por cor/raca",
        "saida": "idade_media_cor",
        "precisa_df": True,
        "requer": [
            (r"\bgroupby\b", "O enunciado pede groupby na variavel COR_RACA."),
        ],
        "checagens": [
            ("um grupo para cada cor/raca da base", _c9_grupos),
            ("as medias de idade conferem", _c9_media),
        ],
    },
    10: {
        "rotulo": "Exercicio 10 — estatisticas por cor/raca com agg",
        "saida": "estatisticas",
        "precisa_df": True,
        "requer": [
            (r"\bgroupby\b", "O enunciado pede groupby na variavel COR_RACA."),
            (
                r"\.agg\s*\(",
                "O enunciado pede agg com mean, median, count, min e max.",
            ),
        ],
        "checagens": [
            ("as colunas sao mean, median, count, min e max", _c10_colunas),
            ("os valores de todas as estatisticas conferem", _c10_valores),
        ],
    },
}


def avaliar(n, imprimir=True):
    """Corrige o exercicio n (1 a 10) lendo a celula do notebook.

    Devolve (ok, total, pontos) para uso do
    verificar_preenchimento_questoes(); imprimir=False suprime a
    saida detalhada.
    """
    if n not in EXERCICIOS:
        print(f"AVISO: exercicio desconhecido ({n!r}). Use avaliar(1) ate avaliar(10).")
        return None

    cfg = EXERCICIOS[n]
    checagens = cfg["checagens"]
    total = len(checagens)

    # 1) localiza o codigo do aluno no historico do notebook
    try:
        codigo = pega_codigo_aluno(n)
    except NameError:
        if imprimir:
            print("ERRO: este corretor so funciona dentro do notebook (Jupyter/Colab).")
        return None
    if codigo is None:
        if imprimir:
            print(f"Ainda nao encontrei nenhuma celula com o marcador '# EXERCICIO {n}'.")
            print(f"Rode a celula do exercicio {n} antes de corrigir.")
        return None

    # 2) modelo ainda com '...'? avisa antes de qualquer coisa
    if tem_pontinhos(codigo):
        if imprimir:
            print("=" * 60)
            print(f"  Corrigindo: {cfg['rotulo']}")
            print("=" * 60)
            print("  Voce ainda nao completou o modelo: substitua cada '...' pelo")
            print("  que falta, rode a celula e chame o corretor de novo.")
        return (0, total, 0.0)

    # 3) valida a sintaxe
    try:
        compile(codigo, f"<exercicio {n}>", "exec")
    except SyntaxError as e:
        if imprimir:
            print(
                f"Erro de SINTAXE na celula do exercicio {n} (linha {e.lineno}): {e.msg}"
            )
            print("Confira os dois-pontos, aspas e a indentacao (4 espacos).")
        return None

    # 4) metodo exigido pelo enunciado (query, groupby, agg)
    for padrao, mensagem in cfg["requer"]:
        if not re.search(padrao, codigo):
            if imprimir:
                print("=" * 60)
                print(f"  Corrigindo: {cfg['rotulo']}")
                print("=" * 60)
                print(f"  [FALHOU] {mensagem}")
                print("  Refaca, rode a celula e chame o corretor de novo.")
            return (0, total, 0.0)

    # 5) carrega a base (exercicio 1 nao precisa)
    df = None
    if cfg["precisa_df"]:
        df = _carregar_df(imprimir)
        if df is None:
            return (0, total, 0.0)

    # 6) executa a celula do aluno (injeta pd e df_poprua quando couber)
    env = {"__name__": "corrigido", "pd": pd}
    if cfg["precisa_df"] and n != 2:
        env["df_poprua"] = df.copy()
    try:
        exec(compile(codigo, f"<exercicio {n}>", "exec"), env)
    except FileNotFoundError:
        if imprimir:
            print(
                f"  [FALHOU] Nao encontrei o arquivo '{ARQUIVO_CSV}' no diretorio"
                " do notebook."
            )
            print("           Rode antes a celula de download (!wget) do Exercicio 2.")
        return (0, total, 0.0)
    except Exception as erro:
        if imprimir:
            print(f"  [FALHOU] {type(erro).__name__} ao executar a sua celula: {erro}")
        return (0, total, 0.0)

    if imprimir:
        print("=" * 60)
        print(f"  Corrigindo: {cfg['rotulo']}")
        print("=" * 60)

    # 7) roda as checagens
    ok = 0
    for desc, fn in checagens:
        try:
            passou = bool(fn(env, df))
        except Exception:
            passou = False
        if passou:
            ok += 1
            if imprimir:
                print(f"  [OK]     {desc}")
        elif imprimir:
            print(f"  [FALHOU] {desc}")
            if not isinstance(env.get(cfg["saida"]), pd.DataFrame) and desc.startswith(
                ("df_poprua_60mais", "df_filtro", "estatisticas")
            ):
                pass  # a checagem de tipo ja explica

    pontos = ok / total * 10.0
    if imprimir:
        print(f"  ({cfg['rotulo']}: {ok}/{total} checagens -> {pontos:.1f} pontos)")
        print("-" * 60)
        print(f"  Nota: {pontos:.1f} / 10   ({ok} de {total} checagens)")
        print("-" * 60)
        if ok == total:
            print("  *** PARABENS! Todas as checagens passaram. ***")
        elif ok == 0:
            print("  Nenhuma checagem passou. Leia as mensagens [FALHOU] acima.")
            print(f"  Confira a variavel-resposta ({cfg['saida']}) e rode a celula dela.")
        else:
            print("  Quase la! Veja acima as checagens que falharam.")
    return (ok, total, pontos)


# ---------------------------------------------------------------------
#  TESTE DOS TESTES — verificacao final da entrega
# ---------------------------------------------------------------------


def verificar_preenchimento_questoes(imprimir=True):
    """Confere se todos os exercícios estão completos e o nome foi preenchido.

    Retorna (lista_ok, nome):
      lista_ok : True se os 10 exercicios passaram em todas as checagens
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
        m = re.search(r'^\s*meu_nome\s*=\s*["\'](.+?)["\']\s*(?:#.*)?$', celula, re.M)
        if m and m.group(1).strip() and set(m.group(1).strip()) != {"."}:
            nome = m.group(1).strip()
            break

    if imprimir:
        print("=" * 60)
        print("  VERIFICACAO FINAL DA ENTREGA — Exercicios 1 a 10")
        print("=" * 60)
        for n, completo in resumo:
            if completo is None:
                print(f"  Exercicio {n}: PENDENTE  (celula nao rodada ou nao encontrada)")
            elif completo:
                print(f"  Exercicio {n}: COMPLETO (todas as checagens passaram)")
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