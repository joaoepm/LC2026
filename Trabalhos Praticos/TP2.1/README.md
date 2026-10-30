# Exercício 1: Game of Life como Máquina de Estados Finita

O [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway's_Game_of_Life) é um exemplo de um autómato celular. Neste problema modifica-se as regras do autómato de forma a usar um espaço de estados finito.

## Enunciado

**a.** O espaço de estados é definido por uma grelha de células booleanas (morta=0/viva=1) de dimensão `N × N` (com `N > 16`) identificadas por índices `(i, j) ∈ {1..N}`. Estas `N²` células são aqui referidas como "normais".

**b.** Inicialmente todas as células normais estão mortas excepto as células `i, j ≤ 3` que estão vivas. Um estado onde todas as células normais estão mortas é um "estado de erro".

**c.** Adicionalmente existem:

1. `2N + 1` "células iniciais" que correspondem a um dos índices, `i` ou `j`, ser zero. As células iniciais têm valores constantes que, no estado inicial, são gerados aleatoriamente com uma probabilidade `1/2` de estarem vivas.
2. `2N + 3` "células finais" que não são iniciais e um dos seus índices tem o valor `N + 1`. As células finais têm valores constantemente `0`; i.e. estão mortas.

**d.** As células normais do autómato modificam o estado de acordo com a regra "B3|S23": i.e. a célula *nasce* (passa de `0` a `1`) se tem exatamente `3` vizinhos vivos; *sobrevive* (mantém-se viva) se o número de vizinhos vivos é `2` ou `3`; caso contrário morre ou continua morta.

**e.** A célula `(i0, j0)` e `(i1, j1)` são vizinhas sse:

```
max(|i0 − i1|, |j0 − j1|) = 1
```

## Pretende-se

**a.** Construir uma máquina de estados finita (**FSM**) que represente este autómato.

Este problema tem duas interpretações possíveis para as transições da FSM:

1. Em cada transição do sistema **uma e só uma** célula normal transita de estado.
2. Em cada transição do sistema **todas as** células normais transitam de estado simultaneamente.

Ambas as opções devem ser contempladas e a relação de transição selecionada é determinada pelo valor de um parâmetro definido no código.

**b.** Provar (ou obter contra-exemplos) as seguintes propriedades:

1. Nunca se alcança o estado de erro.
2. Nenhuma célula normal está permanentemente morta ou permanentemente viva.
