import marimo

__generated_with = "0.25.0"
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
    #disponibilidade = pd.read_csv(DATA_DIR / "disponibilidade_excecoes.csv")

    T = len(turmas)
    D = disciplinas["disciplina"].nunique()
    P = disciplinas["professor"].nunique()
    S = len(salas)
    D, P = 5,6

    return D, P, disciplinas, salas, turmas


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

    for turma in turmas:
        for disciplina in disciplinas:
            for sala in salas:
                for dia in range(D):
                    for periodo in range(P):
                        x[turma, disciplina, sala, dia, periodo] = horario.IntVar(
                            0, 1, f"x_{turma}_{disciplina}_{sala}_{dia}_{periodo}"
                        )
    return (x,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    R1. Uma turma não pode ter duas aulas em simultâneo
    """)
    return


@app.cell
def _(D, P, disciplinas, horario, salas, turmas, x):
    for t in turmas:
        for d in range(D):
            for p in range(P):
                horario.Add(sum(x[t, d, s, d, p] for d in disciplinas for s in salas) <= 1)
    return


if __name__ == "__main__":
    app.run()
