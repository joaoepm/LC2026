import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from pathlib import Path

    return Path, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Trabalho Prático: Gerador de Horário Escolar

    ## Contexto

    Uma escola precisa de gerar automaticamente o horário semanal de um
    conjunto de turmas, respeitando a carga letiva de cada disciplina, a
    disponibilidade dos professores e as salas (normais e especiais,
    partilhadas e em número limitado). Além disso, a escola quer poder
    reagir rapidamente a pequenas alterações de recursos (um professor
    fica indisponível, uma sala avaria, entra uma turma nova) sem ter de
    recomeçar o planeamento do zero.

    Este é um problema de **satisfação e otimização de restrições**
    (CSP/CP). Cabe-te a ti escolher e justificar a técnica de modelação
    e as ferramentas — o enunciado não fornece código de modelação nem
    de apresentação de resultados.

    ## Objetivo

    Construir, num ou mais notebooks Marimo, um sistema que:

    1. importa os dados de entrada de ficheiros (secção "Dados de
       entrada"),
    2. gera um horário que respeite os **requisitos obrigatórios**
       (secção seguinte) e otimize o **objetivo** (buracos),
    3. seja capaz de, a partir de um horário já gerado, produzir
       eficientemente um novo horário válido quando os recursos mudam
       ligeiramente (secção "Construção incremental").
    """)
    return


@app.cell
def _(Path, pd):
    DATA_DIR = Path("dados")

    turmas = pd.read_csv(DATA_DIR/"turmas.csv")
    disciplinas = pd.read_csv(DATA_DIR / "disciplinas.csv")
    salas = pd.read_csv(DATA_DIR / "salas.csv")
    disponibilidade = pd.read_csv(DATA_DIR / "disponibilidade_excecoes.csv")

    disciplinas["carga_semanal"] = pd.to_numeric(
        disciplinas["carga_semanal"].astype(str).str.strip()
    )

    T = len(turmas)
    Di = disciplinas["disciplina"].nunique()
    Po = disciplinas["professor"].nunique()
    S = len(salas)
    D, P = 5,6
    return D, P, disciplinas, disponibilidade, salas, turmas


@app.cell
def _(disciplinas, salas, turmas):
    print("TURMAS")
    print(turmas)

    print("\nDISCIPLINAS")
    print(disciplinas)

    print("\nSALAS")
    print(salas)
    return


@app.cell
def _():
    from ortools.linear_solver import pywraplp

    horario = pywraplp.Solver.CreateSolver('SCIP')
    return (horario,)


@app.cell
def _(D, P, disciplinas, horario, salas, turmas):
    x = {}

    for turma in turmas["turma"]:
        for disciplina in disciplinas["disciplina"]:
            for sala in salas["sala"]:
                for dia in range(D):
                    for periodo in range(P):
                        x[turma, disciplina, sala, dia, periodo] = horario.IntVar(
                            0, 1, f"x_{turma}_{disciplina}_{sala}_{dia}_{periodo}"
                        )
    return (x,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R1.** Uma turma não pode ter duas aulas em simultâneo
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t in turmas["turma"]:
        for d in range(D):
            for p in range(P):
                horario.Add(sum(x[t, di, s, d, p] for di in disciplinas["disciplina"] for s in salas["sala"]) <= 1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R2.** Cada disciplina cumpre *exatamente* a carga semanal definida em `disciplinas.csv`, para cada turma
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t2 in turmas["turma"]:
        for di in disciplinas["disciplina"]:

            carga = disciplinas.loc[
                disciplinas["disciplina"] == di,
                "carga_semanal"
            ].iloc[0]

            horario.Add(
                sum(x[t2, di, sala, dia, periodo] for sala in salas["sala"] for dia in range(D) for periodo in range(P)) == carga)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **R3.** No máximo uma aula da mesma disciplina por dia, por
      turma — exceto disciplinas de duplo período (ver R4), em que o
      bloco de 2 tempos conta como uma só ocorrência nesse dia.
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t3 in turmas["turma"]:
        for di3 in disciplinas.loc[
            disciplinas["duplo_periodo"] == "nao",
            "disciplina"
        ]:
            for dia3 in range(D):

                horario.Add(
                    sum(x[t3, di3, sala3, dia3, periodo3] for sala3 in salas["sala"] for periodo3 in range(P)) <= 1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    O que está a acontecer

    Para cada:

    t3 → turma
    di3 → disciplina normal
    dia3 → dia

    somamos todos os períodos e salas:

    sum(
        x[t3, di3, sala3, dia3, periodo3]
        for sala3 in salas["sala"]
        for periodo3 in range(P)
    )

    e obrigamos:

    <= 1

    Portanto, se Matemática tem:

    Segunda:
      período 1 → Matemática
      período 2 → -
      período 3 → Matemática

    a soma seria 2, logo é proibido.

    Já uma disciplina como Educação Física, que tem duplo_periodo = sim, fica de fora desta restrição e será tratada na R4, onde vamos obrigar os dois períodos a serem consecutivos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **R4.** Disciplinas marcadas `duplo_periodo=sim` só podem ser
      dadas em blocos de 2 tempos consecutivos, no mesmo dia (nunca um
      tempo isolado).
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t4 in turmas["turma"]:
        for di4 in disciplinas.loc[
            disciplinas["duplo_periodo"] == "sim",
            "disciplina"
        ]:
            for dia4 in range(D):

                horario.Add(
                    sum(
                        x[t4, di4, sala4, dia4, 0]
                        for sala4 in salas["sala"]
                    )
                    <=
                    sum(
                        x[t4, di4, sala4, dia4, 1]
                        for sala4 in salas["sala"]
                    )
                )

                horario.Add(
                    sum(
                        x[t4, di4, sala4, dia4, P - 1]
                        for sala4 in salas["sala"]
                    )
                    <=
                    sum(
                        x[t4, di4, sala4, dia4, P - 2]
                        for sala4 in salas["sala"]
                    )
                )

                for periodo4 in range(1, P - 1):

                    horario.Add(
                        sum(
                            x[t4, di4, sala4, dia4, periodo4]
                            for sala4 in salas["sala"]
                        )
                        <=
                        sum(
                            x[t4, di4, sala4, dia4, periodo4 - 1]
                            for sala4 in salas["sala"]
                        )
                        +
                        sum(
                            x[t4, di4, sala4, dia4, periodo4 + 1]
                            for sala4 in salas["sala"]
                        )
                    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    O que isto garante

    Por exemplo, com 6 períodos:

    Período:    1  2  3  4  5  6
                ────────────────
                EF EF

    é permitido.

    Mas isto:

    Período:    1  2  3  4  5  6
                EF    EF

    não é permitido, porque não são consecutivos.

    E isto:

    Período:    1  2  3  4  5  6
                EF

    também não é permitido em conjunto com a R2, porque a R2 exige que Educação Física tenha a carga semanal correspondente (2 no teu exemplo), enquanto a R4 obriga essas ocorrências a aparecerem como um par consecutivo.

    A razão de usarmos:

    range(P - 1)

    é para podermos comparar:

    periodo4

    com:

    periodo4 + 1

    sem tentar aceder a um período que não existe.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **R5.** Um professor não pode dar duas aulas em simultâneo, mesmo
      que sejam a turmas ou disciplinas diferentes.
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for prof5 in disciplinas["professor"].unique():
        for dia5 in range(D):
            for periodo5 in range(P):

                horario.Add(
                    sum(
                        x[turma5, di5, sala5, dia5, periodo5]
                        for turma5 in turmas["turma"]
                        for di5 in disciplinas.loc[
                            disciplinas["professor"] == prof5,
                            "disciplina"
                        ]
                        for sala5 in salas["sala"]) <= 1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R6.** Um professor só pode dar aulas nos tempos em que está
      disponível (`disponibilidade_excecoes.csv`).
    """)
    return


@app.cell
def _(disciplinas, disponibilidade, horario, salas, turmas, x):
    dias = {
        "Seg": 0,
        "Ter": 1,
        "Qua": 2,
        "Qui": 3,
        "Sex": 4
    }

    for _, excecao6 in disponibilidade.iterrows():

        prof6 = excecao6["professor"]
        dia6 = dias[excecao6["dia"]]
        periodo6 = int(excecao6["periodo"]) - 1

        for turma6 in turmas["turma"]:
            for di6 in disciplinas.loc[
                disciplinas["professor"] == prof6,
                "disciplina"
            ]:
                for sala6 in salas["sala"]:

                    horario.Add(x[turma6, di6, sala6, dia6, periodo6] == 0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **R7.** Cada aula ocupa uma sala. Disciplinas com `sala_especial`
      só podem usar salas desse tipo; as restantes usam salas
      `normal`. Em nenhum tempo o número de aulas a decorrer num tipo
      de sala pode exceder a `quantidade` desse tipo definida em
      `salas.csv`.
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t7 in turmas["turma"]:
        for di7 in disciplinas["disciplina"]:
            for dia7 in range(D):
                for periodo7 in range(P):

                    horario.Add(
                        sum(
                            x[t7, di7, sala7, dia7, periodo7]
                            for sala7 in salas["sala"]
                        ) <= 1
                    )
    return


@app.cell
def _(D, P, disciplinas, horario, pd, salas, turmas, x):
    for t72 in turmas["turma"]:
        for di72 in disciplinas["disciplina"]:

            sala_especial72 = disciplinas.loc[
                disciplinas["disciplina"] == di72,
                "sala_especial"
            ].iloc[0]

            if pd.isna(sala_especial72):
                sala_especial72 = "Sala Normal"

            for sala72 in salas["sala"]:

                if sala72 != sala_especial72:
                    for dia72 in range(D):
                        for periodo72 in range(P):

                            horario.Add(
                                x[t72, di72, sala72, dia72, periodo72] == 0
                            )
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for sala73 in salas["sala"]:

        quantidade7 = salas.loc[
            salas["sala"] == sala73,
            "quantidade"
        ].iloc[0]

        for dia73 in range(D):
            for periodo73 in range(P):

                horario.Add(
                    sum(
                        x[t73, di73, sala73, dia73, periodo73]
                        for t73 in turmas["turma"]
                        for di73 in disciplinas["disciplina"]
                    )
                    <= quantidade7
                )
    return


@app.cell
def _(horario):
    status = horario.Solve()

    print("Status:", status)
    return


@app.cell
def _(horario):
    print("Variáveis:", horario.NumVariables())
    print("Restrições:", horario.NumConstraints())
    return


@app.cell
def _(D, P, disciplinas, mo, pd, salas, turmas, x):
    dias_nome = ["Seg", "Ter", "Qua", "Qui", "Sex"]

    tabelas = []

    for turma8 in turmas["turma"]:

        horario_turma8 = []

        for periodo8 in range(P):

            linha8 = {"Período": periodo8 + 1}

            for dia8 in range(D):

                aula8 = ""

                for di8 in disciplinas["disciplina"]:
                    for sala8 in salas["sala"]:

                        if x[
                            turma8,
                            di8,
                            sala8,
                            dia8,
                            periodo8
                        ].solution_value() > 0.5:

                            aula8 = f"{di8} ({sala8})"

                linha8[dias_nome[dia8]] = aula8

            horario_turma8.append(linha8)

        tabela8 = pd.DataFrame(horario_turma8)

        tabelas.append(
            mo.vstack([
                mo.md(f"## Turma {turma8}"),
                mo.ui.table(tabela8)
            ])
        )

    mo.vstack(tabelas)
    return


if __name__ == "__main__":
    app.run()
