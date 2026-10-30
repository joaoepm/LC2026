# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.24.2",
#     "z3-solver",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Resumo do Exercício 1: Game of Life como Máquina de Estados Finita

    ## Contexto & Visão Geral
    O Conway's Game of Life é um autómato celular. Aqui modifica-se para ter um **espaço de estados finito**: uma grelha $N\times N$ ($N>16$) de células normais, rodeada por uma fronteira de células com valores constantes. O objetivo é construir uma **FSM** que represente o autómato e **verificar propriedades** (ou obter contra-exemplos).

    ---

    ## Definição do autómato (do enunciado)
    * **Células normais:** $(i,j)\in\{1..N\}^2$, booleanas (morta=0, viva=1).
    * **Estado inicial:** todas mortas, exceto as de $i,j\le3$ (bloco $3\times3$ vivo).
    * **Estado de erro:** todas as células normais mortas.
    * **Células iniciais** ($2N+1$): as que têm $i=0$ ou $j=0$ (com $i,j\in\{0..N\}$). Valores **constantes**, gerados aleatoriamente com probabilidade $1/2$ de estarem vivas.
    * **Células finais** ($2N+3$): as que não são iniciais e têm um índice $=N+1$. Constantemente **mortas**.
    * **Regra B3/S23:** nasce se tem exatamente 3 vizinhos vivos; sobrevive se tem 2 ou 3; caso contrário morre/continua morta.
    * **Vizinhança:** $\max(|i_0-i_1|,|j_0-j_1|)=1$ (8 vizinhos).

    ---

    ## Objetivos Principais
    1. **Construir a FSM** (estado, estado inicial, relação de transição, estado de erro) com **duas interpretações** escolhidas por um parâmetro `modo`:
       * `"async"`: em cada transição **uma e só uma** célula normal é atualizada;
       * `"sync"`: em cada transição **todas** as células normais são atualizadas simultaneamente.
    2. **Provar (ou obter contra-exemplos)**:
       * (i) nunca se alcança o estado de erro;
       * (ii) nenhuma célula normal está permanentemente morta ou permanentemente viva.

    ---

    ## Decisões de interpretação (convém confirmar com o enunciado/professor)
    * Os cantos $(0,N+1)$ e $(N+1,0)$ são tratados como células **finais** (mortas): têm um índice $=N+1$ e não são iniciais. É o que dá a contagem $2N+3$.
    * As células iniciais são geradas **uma vez** (semente `seed`) e **ficam fixas** durante toda a execução. Os resultados valem para essa fronteira; outra semente pode dar outro resultado (em particular em (i) no modo `sync`).
    * No modo `async`, a célula escolhida (de forma não determinística) passa a ter o valor que a regra B3/S23 dá; pode manter o valor (*stuttering*). As restantes não mudam.
    * **Propriedade (ii)**, leitura adotada (alcançabilidade): uma célula é *permanentemente morta* se **não está viva em nenhum estado alcançável**, e *permanentemente viva* se **não está morta em nenhum estado alcançável**. Um contra-exemplo nesta leitura também o é na leitura mais forte ("morta a partir de certo ponto"); já uma prova nesta leitura não prova a mais forte.

    ---

    ## Método
    *Bounded model checking* com Z3: desdobra-se a transição $K$ vezes e pergunta-se se existe um estado "mau" até ao passo $K$. Se existir, o traço é um **contra-exemplo**; testa-se $t=0,1,\dots$ por ordem, por isso o primeiro $t$ é a profundidade mínima.

    ---

    ## Validação e Testes Automáticos
    1. Contagem das células iniciais ($2N+1$) e finais ($2N+3$).
    2. Regra B3/S23 em padrões conhecidos (blinker, bloco), verificada no próprio modelo Z3.
    3. A trajetória do modelo Z3 coincide com a simulação em Python (`sync`).
    4. No modo `async`, nenhuma transição altera duas células.
    5. O traço do BMC em `async` ($N=4$) termina no estado de erro e cada passo altera no máximo uma célula.
    """)
    return


if __name__ == "__main__":
    app.run()
