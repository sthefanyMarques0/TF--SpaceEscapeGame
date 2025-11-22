🛸 SPACE ESCAPE — Alpha 0.3

Space Escape é um jogo arcade desenvolvido em Python + Pygame, onde o jogador controla uma nave espacial que deve desviar de meteoros, atirar para destruí-los, coletar vidas extras e avançar por diferentes níveis até alcançar a pontuação final para vencer.

Este projeto foi desenvolvido com fins acadêmicos, seguindo a estrutura sugerida pelo Prof. Filipo Novo Mor.
-----------------------------------------------------
Alunos: 
Sthefany Marques da Fonseca, user: sthefanyMarques0
João Madruga, user: JPMadruga01

---------------------------------------------------
🛠️ Instalação
1️⃣ Clone o repositório
git clone https://github.com/sthefanyMarques0/TF--SpaceEscapeGame.git
cd TF--SpaceEscapeGame

------------------------------------------------------

📦 Configuração
2️⃣ Instale as dependências

O jogo utiliza a biblioteca Pygame.

pip install pygame

▶️ Como Executar
python space_escape.py
--------------------------------------------------------

🛠️ Compilação (Opcional)

Se quiser gerar um executável (.exe) para Windows:

pip install pyinstaller
pyinstaller --onefile --windowed main.py


O executável será criado em:

/dist/main.exe
-------------------------------------------------
🖥️ Requisitos

Python 3.10+

Pygame instalado
-----------------------------------------------------
🎮 Descrição do Jogo

Você controla uma nave espacial com o mouse e deve:

Desviar de meteoros.

Coletar meteoros verdes para ganhar vidas.

Atirar (clique esquerdo / espaço) para destruir meteoros.

Subir de nível conforme acumula pontos.

Sobreviver até alcançar a pontuação de vitória.

Game Over: quando as vidas atingem 0.
Vitória: ao alcançar 30 pontos.
--------------------------------------------------------
🧩 Funcionalidades Principais

 Controle do Jogador

Movimento pelo mouse

Tiros com clique esquerdo ou barra de espaço

Cooldown entre disparos

 Meteoros

Meteoros normais

Meteoros verdes (+1 vida)

Animação por múltiplos frames

Progressão de Níveis

A dificuldade cresce com o avanço da pontuação

 Sistema de Salvamento

Arquivos utilizados:

savegame.json

highscores.txt

Salvamento automático de:

Pontos

Vidas

Nível

Posição

Sons e Música

Efeitos para tiros e colisões

Música de fundo

Fallback caso o dispositivo não suporte áudio

Interface

Tela inicial

Menu de continuação

Tela de vitória

Tela de derrota

HUD com pontos, vidas e nível

--------------------------------------------------------

# imagem da tabela de Niveis, Velocidade dos meteoros e pontos


------------------------------------------------------

🗂️ Estrutura de Arquivos
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

---------------------------------------------------------

🕹️ Controles
Ação	Comando
Mover nave	Mouse
Atirar	Clique esquerdo / Barra de espaço
Sair	ESC
---------------------------------------------------------

📈 Pontuação

Desviar meteoro → +1 ponto

Destruir meteoro → +2 pontos

Coletar meteoro verde → +1 vida

Vitória ao atingir → 30 pontos
-------------------------------------------------------------

 Itens ATENDIDOS 
Nº	Item da lista	Atende?	Justificativa
1	Criar 3 fases distintas	
2	Determinar condições de vitória	
4	Permitir que o mouse controle a nave	
5	Salvar High Scores e mostrar na intro	
6	Fundo muda conforme o nível	
7	Animar meteoros	
9	Criar meteoro que retira vida ao colidir
12	Meteoros que dão vida extra	
14	Nave controlada por mouse	
16	Jogador pode atirar	
19	Som ao colidir	✔️	sound_hit
20	Som ao ganhar pontos	✔️	sound_point
21	Tela de vitória e derrota	✔️	victory_screen e defeat_screen.
22	Tela de introdução	✔️	show_intro_screen()
------------------------------------------------------------

🗃️ Arquitetura Interna

make_meteors() – cria meteoros

set_level() – ajusta nível e dificuldade

save_game() / load_game() – persistência de dados

update_highscores() – atualização do ranking

Loops principais:

Eventos

Atualização

Renderização
---------------------------------------------------

🏆 Objetivo Final

Sobreviver, evoluir entre os níveis e alcançar 30 pontos para completar o jogo.
------------------------------------------------------------
✨ Dinâmicas do Jogo

Pontuação progressiva

Aumento automático de nível

Colisão e perda de vidas

Animação contínua dos meteoros

Salvamento de progresso

Música e efeitos sonoros

Projéteis com cooldown

Dificuldade crescente
----------------------------------------------------------
📌 Créditos

Professor: Filipo Novo Mor
GitHub: github.com/ProfessorFilipo

Assets:

Música por Maksym Malko (Pixabay)

Demais imagens e sons utilizados no projeto

----------------------------------------------------------

📄 Licença

Projeto desenvolvido exclusivamente para fins acadêmicos e educacionais.

-------------------------------------------------------------
