# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.2",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


@app.cell
def _():
    mo.md(r"""
    # 🧩 Resumo do Trabalho Prático: Sudoku Genérico como CSP

    ## 📋 Contexto & Visão Geral
    O Sudoku é um exemplo clássico de um **Problema de Satisfação de Restrições (CSP)**. Em vez de codificar regras rígidas para linhas, colunas ou blocos de forma isolada, o objetivo deste trabalho é **abstrair a regra fundamental do Sudoku**: qualquer grupo de células pertence a um conjunto onde todos os valores têm de ser distintos (**AllDifferent**) e alguns valores podem estar previamente fixados (pistas).

    Com esta abstração, linhas, colunas, blocos $n \times n$, pistas iniciais e até variantes (diagonais, hiper-sudoku, etc.) passam a ser tratados exatamente da mesma forma pelo solver.

    ---

    ## 🎯 Objetivos Principais
    1. **Modelar** a abstração genérica de um grupo de células com a restrição "todos diferentes" (`box`).
    2. **Especializar** a classe genérica para construir blocos $n \times n$ (`cube`) e sequências retas horizontais/verticais (`path`).
    3. **Gerar pistas aleatórias** de forma paramétrica para criar tabuleiros de jogo.
    4. **Resolver** a grelha $n^2 \times n^2$ montando e satisfazendo o modelo CSP com o **OR-Tools (CP-SAT)**.
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## 🛠️ Requisitos Obrigatórios (R1 a R6)

    * **`box` — Grupo Genérico (R1):**
      * Guarda um mapeamento `(linha, coluna) → valor ou None`.
      * Método `add(i, j, val=None)` que adiciona células ao grupo e **rejeita** (levanta exceção) limites fora da grelha ou valores fora do intervalo $[1, n^2]$.
      * Método para exportar a representação como matriz $n^2 \times n^2$.
      * *Não sabe nada sobre Sudoku — apenas gere um grupo de células.*

    * **`cube` e `path` — Especializações (R2 & R3):**
      * **R2 (`cube`):** Constrói o bloco $n \times n$ para os índices de bloco $(i, j)$.
      * **R3 (`path`):** Constrói o troço reto (linha ou coluna) entre duas coordenadas `inicio` e `fim` (funciona em qualquer sentido).

    * **`gerar_pistas` — Pistas Aleatórias (R4):**
      * Função que devolve um `box` com $k$ células escolhidas aleatoriamente na grelha e fixadas a valores válidos $[1, n^2]$.

    * **Modelo e Resolução CSP (R5 & R6):**
      * **R5:** Modelo CSP com uma variável por célula $X_{i,j} \in [1, n^2]$. Aceita um número arbitrário de grupos (`box`, `cube`, `path`, pistas) e aplica a restrição `AllDifferent` e valores fixos.
      * **R6:** Junta todas as linhas, colunas, blocos $n \times n$ e o grupo de pistas para resolver a grelha.
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## 🧪 Validação e Testes Automáticos
    O notebook (ou módulo de testes) deve validar automaticamente:
    1. **Integridade da Solução:** Confirmar que linhas, colunas e blocos contêm todos os valores de $1 \ldots n^2$ sem repetições.
    2. **Preservação de Pistas:** Garantir que os valores fixos gerados aleatoriamente se mantêm na solução final.
    3. **Validação de Limites:** Confirmar que `add(...)` rejeita coordenadas ou valores inválidos.
    4. **Generalização de Dimensão:** Executar o fluxo completo para $n=3$ ($9 \times 9$) e para outro valor como $n=2$ ($4 \times 4$) para provar que a solução não está *hardcoded*.

    ---

    ## 🌟 Extensões Opcionais (Bónus)
    * **X-Sudoku (Diagonal):** Adicionar as duas diagonais principais como grupos `box` com restrição `AllDifferent`.
    * **Hyper-Sudoku / Windoku:** Adicionar 4 blocos sobrepostos suplementares.
    * **Jigsaw / Sudoku Irregular:** Criar regiões de forma arbitrária como `box`.
    * **Sudoku 3D:** Estender a estrutura para grelhas $n^2 \times n^2 \times n^2$.
    """)
    return


@app.cell
def _():
    import random
    from ortools.sat.python import cp_model

    #1. Grupo generico (R1) - dicionario + funcoes
    #Uma box é um dicionario:
    #{'name': str, 'n': int, 'cells': {(i,j):valor ou None}}
    #None = celula livre; Int = celula fixa a esse valor
    #Nao se sabe nada de linhas, colunas, blocos

    def novo_box(n, name = "box", cells = None):
        """R1: cria um box vazio ou com cells iniciais validadas via box_add"""
        box = {'name': name, 'n': n, 'cells': {}}
        if cells:
            for (i,j), val in cells.items():
                box_add(box, i, j, val)
        return box

    def box_add(box, i, j, val=None):
        """R1: acrescenta (i, j) ao box, opcionalmente fixa a val
        Dá ValueError se as coordenadas ou valor forem inválidos"""
        n2 = box['n'] ** 2
        if not (0 <= i < n2 and 0 <= j < n2):
            raise ValueError(f"Célula ({i},{j}) fora da grelha {n2}x{n2}.")
        if val is not None and not (1 <= val <= n2):
            raise ValueError(f"Valor {val} fora do intervalo [1,{n2}].")
        box['cells'][(i, j)] = val


    def box_matriz(box):
        """R1: matriz n^2 x n^2 com 0 nas células não fixas/fora do box e o valor fixo nas restantes"""
        n2 = box['n'] ** 2
        m = [[0] * n2 for _ in range(n2)]
        for (i, j), v in box['cells'].items():
            m[i][j] = v if v is not None else 0
        return m


    # 2. Formas concretas (R2, R3) e Pistas (R4)

    def generate_cube(n, i, j):
        """R2: box do bloco n x n de índices de bloco (i, j), 0 <= i, j < n. Canto superior esquerdo = (i*n, j*n)"""
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"Índices de bloco ({i},{j}) fora de [0,{n - 1}].")
        box = novo_box(n, f"bloco_{i}_{j}")
        for di in range(n):
            for dj in range(n):
                box_add(box, i * n + di, j * n + dj)
        return box


    def generate_path(n, inicio, fim):
        """R3: box com o troço reto (horizontal ou vertical) entre inicio e fim, inclusive, em qualquer sentido"""
        (i0, j0), (i1, j1) = inicio, fim
        if i0 != i1 and j0 != j1:
            raise ValueError("inicio e fim têm de estar na mesma linha ou coluna.")
        box = novo_box(n, f"path_{inicio}_{fim}")
        if i0 == i1:
            passo = 1 if j1 >= j0 else -1
            for j in range(j0, j1 + passo, passo):
                box_add(box, i0, j)
        else:
            passo = 1 if i1 >= i0 else -1
            for i in range(i0, i1 + passo, passo):
                box_add(box, i, j0)
        return box


    def gerar_pistas(n, k=None):
        """R4: box com k células aleatórias fixas a valores distintos em [1, n^2]. k por omissão = n. Os valores são distintos porque o grupo de pistas também é all-different."""
        n2 = n * n
        if k is None:
            k = n
        if not (0 <= k <= n2):
            raise ValueError(f"k={k} inválido: máximo {n2} pistas.")
        box = novo_box(n, "pistas_aleatorias")
        todas = [(i, j) for i in range(n2) for j in range(n2)]
        celulas = random.sample(todas, k)
        valores = random.sample(range(1, n2 + 1), k)
        for (i, j), v in zip(celulas, valores):
            box_add(box, i, j, v)
        return box


    # 3. Modelo CSP (R5)

    solucao = "solucao"
    sem_solucao = "sem_solucao"
    desconhecido = "desconhecido"  #timeout: nao significa insoluvel


    def build_and_solve(n, boxes, time_limit_s=10):
        """R5: uma variável por célula em [1, n^2]; para cada box impõe
        all-different e fixa as células com valor
        Devolve (grelha, estado): grelha é dict {(i,j): valor} ou None;
        estado é solucao, sem_solucao ou desconhecido"""
        n2 = n * n

        # fixos globais; deteta conflitos entre boxes
        fixos = {}
        for box in boxes:
            for pos, v in box['cells'].items():
                if v is None:
                    continue
                if pos in fixos and fixos[pos] != v:
                    return None, sem_solucao  # duas pistas incompatíveis
                fixos[pos] = v

        model = cp_model.CpModel()
        vars_map = {}
        for box in boxes:
            for pos in box['cells']:
                i, j = pos
                if not (0 <= i < n2 and 0 <= j < n2):
                    raise ValueError(f"Célula {pos} fora da grelha {n2}x{n2}.")
                if pos not in vars_map:
                    vars_map[pos] = model.NewIntVar(1, n2, f"x_{i}_{j}")

        for pos, v in fixos.items():
            model.Add(vars_map[pos] == v)

        for box in boxes:
            model.AddAllDifferent([vars_map[pos] for pos in box['cells']])

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_s
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {pos: solver.Value(var) for pos, var in vars_map.items()}, solucao
        if status == cp_model.INFEASIBLE:
            return None, sem_solucao
        return None, desconhecido



    # 4. Montagem do sudoku (R6)

    def montar_sudoku_completo(n, pistas_box):
        """Linhas + colunas + blocos + pistas"""
        n2 = n * n
        boxes = [pistas_box]
        for i in range(n2):
            boxes.append(generate_path(n, (i, 0), (i, n2 - 1)))   # linha i
            boxes.append(generate_path(n, (0, i), (n2 - 1, i)))   # coluna i
        for i in range(n):
            for j in range(n):
                boxes.append(generate_cube(n, i, j))
        return boxes


    def resolver_sudoku(n, k=None, max_tentativas=50, time_limit_s=10):
        """Gera pistas aleatórias e resolve. Se o puzzle não tiver solução,
        tenta novas pistas (até max_tentativas), porque pistas aleatórias
        podem ser contraditórias e queremos sempre devolver um puzzle solúvel.
        Devolve (grelha, pistas_box, estado)."""
        estado = sem_solucao
        for _ in range(max_tentativas):
            pistas = gerar_pistas(n, k)
            grelha, estado = build_and_solve(n, montar_sudoku_completo(n, pistas), time_limit_s)
            if estado == solucao:
                return grelha, pistas, estado
        return None, None, estado



    # 5. Validacao automatica

    def validar_solucao(n, grelha, pistas_box):
        """Levanta AssertionError se a solução for inválida"""
        n2 = n * n
        esperado = set(range(1, n2 + 1))
        for i in range(n2):
            assert {grelha[(i, j)] for j in range(n2)} == esperado, f"linha {i} inválida"
            assert {grelha[(j, i)] for j in range(n2)} == esperado, f"coluna {i} inválida"
        for bi in range(n):
            for bj in range(n):
                vals = {grelha[(bi * n + di, bj * n + dj)] for di in range(n) for dj in range(n)}
                assert vals == esperado, f"bloco ({bi},{bj}) inválido"
        for pos, v in pistas_box['cells'].items():
            assert grelha[pos] == v, f"pista {pos}={v} não respeitada"


    def testar_box_add():
        n = 3
        b = novo_box(n)
        box_add(b, 0, 0, 5)
        box_add(b, 1, 1)
        assert b['cells'] == {(0, 0): 5, (1, 1): None}
        assert box_matriz(b)[0][0] == 5 and box_matriz(b)[1][1] == 0
        for args in [(9, 0, 1), (0, 9, 1), (-1, 0, 1), (0, -1, 1), (0, 0, 0), (0, 0, 10)]:
            try:
                box_add(b, *args)
            except ValueError:
                continue
            raise AssertionError(f"box_add{args} devia ter sido rejeitado")
        print("✓ box_add rejeita coordenadas e valores inválidos")


    def testar_formas():
        n = 3
        assert sorted(generate_cube(n, 1, 2)['cells']) == sorted(
            (3 + di, 6 + dj) for di in range(3) for dj in range(3))
        assert list(generate_path(n, (2, 0), (2, 3))['cells']) == [(2, 0), (2, 1), (2, 2), (2, 3)]
        assert list(generate_path(n, (2, 3), (2, 0))['cells']) == [(2, 3), (2, 2), (2, 1), (2, 0)]
        assert list(generate_path(n, (0, 4), (2, 4))['cells']) == [(0, 4), (1, 4), (2, 4)]
        assert list(generate_path(n, (2, 4), (0, 4))['cells']) == [(2, 4), (1, 4), (0, 4)]
        print("✓ cube e path corretos (nos dois sentidos)")


    def testar_conflito_e_insolucao():
        n = 3
        a = novo_box(n, cells={(0, 0): 1})
        b = novo_box(n, cells={(0, 0): 2})
        _, estado = build_and_solve(n, [a, b])
        assert estado == sem_solucao
        # duas células na mesma linha com o mesmo valor
        c = novo_box(n, cells={(0, 0): 4, (0, 1): 4})
        d = generate_path(n, (0, 0), (0, 8))
        _, estado = build_and_solve(n, [c, d])
        assert estado == sem_solucao
        print("✓ conflitos devolvem sem_solucao")


    def testar_fluxo(n):
        grelha, pistas, estado = resolver_sudoku(n)
        assert estado == solucao, f"sem solução para n={n} ({estado})"
        validar_solucao(n, grelha, pistas)
        print(f"✓ fluxo completo n={n} ({n * n}x{n * n}) validado")
        return grelha, pistas


    def imprimir_grelha(n, grelha):
        """Imprime uma grelha dada como dict {(i,j): valor ou None}
        Células sem valor aparecem como '.' """
        n2 = n * n
        larg = len(str(n2))
        for i in range(n2):
            partes = []
            for j0 in range(0, n2, n):
                valores = []
                for j in range(j0, j0 + n):
                    v = grelha.get((i, j))
                    texto = "." if v is None else str(v)
                    valores.append(texto.rjust(larg))
                partes.append(" ".join(valores))
            print(" | ".join(partes))
            if (i + 1) % n == 0 and i + 1 != n2:
                print("-+-".join("-" * (n * (larg + 1) - 1) for _ in range(n)))


    if __name__ == "__main__":
        testar_box_add()
        testar_formas()
        testar_conflito_e_insolucao()
        testar_fluxo(2)
        testar_fluxo(3)

        # Demonstração, trocar valor do k para mudar o numero de pistas até 9
        g, p, estado = resolver_sudoku(3, k=9)
        assert estado == solucao
        validar_solucao(3, g, p)

        print("\nPuzzle inicial (só as pistas):")
        imprimir_grelha(3, p['cells'])

        print("\nSolução:")
        imprimir_grelha(3, g)
    return


if __name__ == "__main__":
    app.run()
