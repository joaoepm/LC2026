# Exercício 2

> *Este exercício é um problema de optimização não linear cónica que deve ser resolvido com a interface `cvxpy` e um dos "solvers" `Clarabel` ou `Mosek`.*
>
> *Note que o `Clarabel` não lida com variáveis inteiras e requer a codificação de um algoritmo de relaxação (e.g. "branch-and-bound") para proceder à optimização com inteiros.*
>
> *Por seu lado, a instalação do `Mosek` requer que se obtenha previamente uma licença de estudante.*

Em criptografia pós-quântica é importante um tipo de subconjuntos do espaço métrico `ℝᵐ` designados por *reticulados euclidianos*. Cada espaço é determinado por uma *base* de `k` vetores

```
G ≡ { g₁, g₂, …, g_k | gᵢ ∈ ℝᵐ }
```

*linearmente independentes*. O reticulado determinado por `G` é o conjunto de todas as combinações lineares inteiras dos vetores `gᵢ`. Isto é

```
L_G ≡ { x = z₁ g₁ + z₂ g₂ + … + z_k g_k | zᵢ ∈ ℤ }
```

O problema difícil que está na base de muitas das técnicas criptográficas pós-quânticas designa-se por *Closest Vector Problem* (CVP) e define-se

> *Dado um vetor aleatório* `t ∈ ℝᵐ` *(o "target") e um reticulado determinado pela base* `G`*, calcular o vetor do reticulado* `x ∈ L_G = Σᵢ zᵢ gᵢ` *(com i = 1..k) que está mais próximo de* `t`*.*

Neste exercício vamos considerar uma versão particular deste problema, caracterizada pelas seguintes restrições:

* proximidade define-se pela distância Euclidiana no espaço `ℝᵐ`; isto é

  ```
  dist(x, t) ≡ √( Σⱼ (xⱼ − tⱼ)² )      com j = 1..m
  ```

  sendo `xⱼ` a `j`-ésima componente do vector `x`.

* Os elementos `{g_i,j}` do vector `gᵢ` assim como os elementos `tⱼ` do "target" `t` representam probabilidades; por isso são sempre valores reais no intervalo `[0, 1]` que aqui são gerados aleatoriamente.

* Existe um limite `ℓ` positivo não-nulo nos coeficientes inteiros `zᵢ` tal que, para todo `i = 1..k` se verifica `−ℓ ≤ zᵢ ≤ ℓ`.

* É necessário verificar se os `{gᵢ}` (com i = 1..k) formam realmente uma base.

Nestas circunstâncias pretende-se usar programação cónica para resolver o CVP.

> *Em problemas CVP criptograficamente seguros, os valores típicos de* `m` *e* `k` *são da ordem das centenas. Aqui vamos considerar uma situação simples em que* `k ∼ 16`*,* `m ∼ 2k` *e* `ℓ ∈ {1, 2, 3}`*.*
