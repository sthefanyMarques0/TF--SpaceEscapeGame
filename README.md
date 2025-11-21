# 🛸 SPACE ESCAPE --- Alpha 0.3

Space Escape é um jogo arcade desenvolvido em **Python + Pygame**, onde
o objetivo é **desviar de meteoros**, sobreviver o máximo possível e
progredir por diferentes níveis enquanto coleta vidas extras e dispara
projéteis para destruir obstáculos.

Este projeto foi criado com fins didáticos, seguindo a estrutura
sugerida pelo **Prof. Filipo Novo Mor**.

------------------------------------------------------------------------

## 🎮 Descrição do Jogo

Você controla uma nave espacial usando o **mouse**.
Seu objetivo é:

-   **Desviar dos meteoros** que caem do topo da tela.
-   **Coletar meteoros verdes** para ganhar vidas extras.
-   **Atirar** em meteoros para destruí-los e ganhar pontos adicionais.

-   Subir de nível conforme a pontuação aumenta.
-   Sobreviver até alcançar a pontuação final de vitória.

Colidir com meteoros reduz suas vidas.
Se as vidas chegarem a 0 → **Game Over**.
Se alcançar a pontuação necessária → **Vitória**.

------------------------------------------------------------------------

## 🧩 Funcionalidades Principais

### ✅ Controle do Jogador

-   Movimento controlado pelo **mouse**
-   Tiros com **botão esquerdo** ou **barra de espaço**
-   Cooldown entre disparos

### ✅ Meteoros

-   Meteoros normais
-   Meteoros verdes que concedem **+1 vida**
-   Animação baseada em múltiplos frames

### ✅ Progressão de Níveis

     ![Tabela_do_jogo](Tabela_do_jogo.png)   

### ✅ Sistema de Salvamento

Arquivos usados: - `savegame.json` - `highscores.txt`

Salva automaticamente: - Pontos\
- Vidas\
- Nível\
- Posição

### ✅ Sons e Música

-   Efeitos de pontos e colisão\
-   Música de fundo\
-   Fallback automático caso o dispositivo não suporte áudio

### ✅ Interface

-   Tela inicial\
-   Menu de continuação\
-   Tela de vitória\
-   Tela de derrota\
-   HUD com Pontos, Vidas e Nível

------------------------------------------------------------------------

## 🗂️ Estrutura de Arquivos

    ├── space_escape.py
    ├── savegame.json
    ├── highscores.txt
    ├── nave001.png
    ├── meteoro001.png
    ├── meteoro_vida.png
    ├── fundo_espacial1.png
    ├── fundo_espacial2.jpg
    ├── fundo_espacial3.png
    └── assets de som

------------------------------------------------------------------------

## 🖥️ Requisitos

### Tecnologias:

-   **Python 3.10+**
-   **Pygame**

Instale as dependências:

``` bash
pip install pygame
```

------------------------------------------------------------------------

## ▶️ Como Executar

``` bash
python space_escape.py
```

------------------------------------------------------------------------

## 🕹️ Controles

  Ação         Comando
  ------------ -----------------------------------
  Mover nave   Mouse
  Atirar       Clique esquerdo / Barra de espaço
  Sair         ESC

------------------------------------------------------------------------

## 📈 Pontuação

-   Desviar meteoro → **+1 ponto**\
-   Destruir com tiro → **+2 pontos**\
-   Coletar meteoro de vida → **+1 vida**\
-   Vitória ao atingir: **30 pontos**

------------------------------------------------------------------------

## 🗃️ Arquitetura Interna

-   `make_meteors()` -- cria meteoros\
-   `set_level()` -- muda fase e ajustes\
-   `save_game()` / `load_game()` -- salvamento\
-   `update_highscores()` -- ranking\
-   Loops principais de eventos, atualização e renderização

------------------------------------------------------------------------

## 🏆 Objetivo Final

**Sobreviver**, evoluir de fase e alcançar **30 pontos** para escapar
dos meteoros.

------------------------------------------------------------------------

## 📌 Créditos

**Professor Filipo Novo Mor**\
GitHub: *github.com/ProfessorFilipo*

------------------------------------------------------------------------
