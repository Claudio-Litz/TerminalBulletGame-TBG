import os
import random
import time

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"

PROMPTS_BASE = [
    "O verdadeiro motivo pelo qual {alvo} sumiu por 3 dias sem mandar mensagem.",
    "A pior coisa que você pode sussurrar no ouvido do padre no confessionário.",
    "O título da biografia não autorizada de {alvo}.",
    "A desculpa mais esfarrapada para chegar 4 horas atrasado no trabalho.",
    "Se {alvo} fosse preso amanhã, qual seria a acusação mais provável?",
    "Uma frase perfeitamente aceitável num churrasco, mas terrível no primeiro encontro.",
    "O pior nome possível para uma clínica veterinária.",
    "O que {alvo} pesquisou no Google às 03:42 da madrugada.",
    "A pior coisa para se dizer logo depois de um beijo demorado.",
    "Se {alvo} abrisse um canal no YouTube hoje, qual seria o tema do primeiro vídeo?",
    "A tatuagem mais humilhante que alguém poderia ser obrigado a fazer na testa.",
    "O que você jamais deveria gritar dentro de um avião na decolagem.",
    "O superpoder mais inútil e vergonhoso que o {alvo} poderia ter.",
    "Um novo sabor de pizza que deveria ser proibido pela Convenção de Genebra.",
    "O que {alvo} diria para tentar convencer um ladrão a não roubá-lo.",
    "A pior mensagem para mandar por engano no grupo da família.",
    "O que os alienígenas disseram logo depois de abduzirem e devolverem {alvo}.",
    "O nome de um perfume feito à base do suor de {alvo}.",
    "A pior coisa para se encontrar no bolso de um casaco de brechó.",
    "Uma péssima frase de consolo para dizer a alguém no velório.",
    "O que {alvo} realmente faz quando diz que está 'ocupado estudando'.",
    "A pior justificativa para terminar um namoro de 5 anos.",
    "O que você não deve responder quando a polícia pergunta: 'Sabe por que te parei?'",
    "O nome de um restaurante onde ninguém deveria confiar na higiene dos pratos.",
    "Se {alvo} criasse uma religião própria, qual seria o primeiro mandamento?",
    "A pior ideia de fantasia de casal para ir numa festa da firma.",
    "O maior segredo que {alvo} esconde até dos melhores amigos.",
    "O que nunca falar na reunião de condomínio.",
    "A pior coisa para colocar no currículo profissional.",
    "A última coisa que você espera ouvir do seu médico antes da anestesia geral."
]

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def pausar(s=1.2):
    time.sleep(s)

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.pontos = 0
        self.vitorias_epicas = 0

class JogoTribunal:
    def __init__(self, nomes, meta_pontos=5):
        self.jogadores = [Jogador(n) for n in nomes]
        self.meta_pontos = meta_pontos
        self.rodada = 1
        self.idx_juiz = 0
        self.prompts = list(PROMPTS_BASE)
        random.shuffle(self.prompts)

    def proximo_prompt(self):
        if not self.prompts:
            self.prompts = list(PROMPTS_BASE)
            random.shuffle(self.prompts)
        
        texto = self.prompts.pop()
        # Sorteia um dos amigos para virar o alvo da pergunta
        alvo_nome = random.choice(self.jogadores).nome
        return texto.replace("{alvo}", f"{C_YELLOW}{alvo_nome}{C_RESET}")

    def mostrar_placar(self):
        print(f"{C_BOLD}{C_MAGENTA}==================== TRIBUNAL DO CAOS ===================={C_RESET}")
        print(f"  RODADA {self.rodada} | Meta de Vitória: {self.meta_pontos} Votos")
        print("----------------------------------------------------------")
        placar_str = " | ".join([f"{C_BOLD}{j.nome}{C_RESET}: {C_CYAN}{j.pontos} pts{C_RESET}" for j in self.jogadores])
        print("  " + placar_str)
        print(f"{C_BOLD}{C_MAGENTA}=========================================================={C_RESET}\n")

    def coletar_resposta(self, jogador, pergunta):
        limpar()
        self.mostrar_placar()
        print(f"🔒 {C_RED}{C_BOLD}ZONA SECRETA - APENAS {jogador.nome.upper()} NA FRENTE DA TELA!{C_RESET}")
        print("Os outros jogadores devem VIRAR DE COSTAS ou sair de perto agora.\n")
        input(f"Quando estiver sozinho, {jogador.nome}, aperte ENTER para ver o tema...")

        limpar()
        self.mostrar_placar()
        print(f"Autor: {C_BOLD}{C_YELLOW}{jogador.nome}{C_RESET}")
        print(f"\n{C_BOLD}PERGUNTA:{C_RESET} {pergunta}\n")
        print(f"{C_CYAN}Escreva a resposta mais engraçada, absurda ou ofensiva que conseguir pensar:{C_RESET}")
        
        resposta = ""
        while not resposta.strip():
            resposta = input("✍️  > ").strip()

        limpar()
        print(f"{C_GREEN}✔ Resposta registrada com sucesso!{C_RESET}")
        print(f"\n{C_YELLOW}Aperte ENTER para limpar o terminal e passar o teclado.{C_RESET}")
        input()
        limpar()
        return resposta

    def executar_rodada(self):
        juiz = self.jogadores[self.idx_juiz]
        # Pega dois debatedores para o duelo da rodada
        candidatos = [j for j in self.jogadores if j != juiz]
        # Se houver mais de 2 não-juízes, sorteia 2 para o embate
        duelo = random.sample(candidatos, 2)
        j1, j2 = duelo[0], duelo[1]

        pergunta = self.proximo_prompt()

        # Coleta secreta de cada jogador
        resp1 = self.coletar_resposta(j1, pergunta)
        resp2 = self.coletar_resposta(j2, pergunta)

        # Embaralha as respostas para o Juiz não saber de quem é cada uma
        pacote = [(j1, resp1), (j2, resp2)]
        random.shuffle(pacote)

        # Fase de Julgamento Aberto
        limpar()
        self.mostrar_placar()
        print(f"📢 {C_BOLD}{C_YELLOW}CHAMANDO TODO MUNDO DE VOLTA PARA A MESA!{C_RESET}")
        print(f"Juiz da Rodada: {C_BOLD}{C_RED}{juiz.nome.upper()}{C_RESET}\n")
        print(f"{C_BOLD}TEMA DO DEBATE:{C_RESET}")
        print(f">>> {C_BOLD}{pergunta}{C_RESET}\n")
        print("=" * 58)
        print(f"{C_BOLD}[OPÇÃO 1]{C_RESET} \"{pacote[0][1]}\"\n")
        print(f"{C_BOLD}[OPÇÃO 2]{C_RESET} \"{pacote[1][1]}\"")
        print("=" * 58)
        print(f"\n{juiz.nome}, leia as duas respostas em voz alta para a sala!")

        escolha = ""
        while escolha not in ["1", "2"]:
            escolha = input(f"\n{juiz.nome}, escolha a MELHOR resposta ([1] ou [2]): ").strip()

        idx_vencedor = int(escolha) - 1
        vencedor_autor, resp_vencedora = pacote[idx_vencedor]
        perdedor_autor, resp_perdedora = pacote[1 - idx_vencedor]

        vencedor_autor.pontos += 1

        limpar()
        self.mostrar_placar()
        print(f"{C_GREEN}{C_BOLD}🏆 O Veredito de {juiz.nome} foi proclamado!{C_RESET}\n")
        print(f"Resposta Campeã:\n\"{C_YELLOW}{resp_vencedora}{C_RESET}\"")
        print(f"👉 Autoria de: {C_BOLD}{C_GREEN}{vencedor_autor.nome.upper()}{C_RESET}! (+1 Ponto)\n")
        
        print(f"Resposta Derrotada:\n\"{resp_perdedora}\"")
        print(f"👉 Escrita por: {C_BOLD}{C_RED}{perdedor_autor.nome.upper()}{C_RESET}\n")

        # Comentário dinâmico do sistema
        piadas = [
            f"A sala inteira sabe que {perdedor_autor.nome} tentou demais e falhou miseravelmente.",
            f"Essa resposta de {vencedor_autor.nome} já garante uma vaga no inferno.",
            f"Se a polícia lesse o que {vencedor_autor.nome} escreveu, a partida acabava agora.",
            f"{perdedor_autor.nome} precisa urgentemente rever seu senso de humor.",
            f"Uma decisão justa. A vergonha alheia de {perdedor_autor.nome} foi histórica."
        ]
        print(f"💬 {C_CYAN}{random.choice(piadas)}{C_RESET}")

        self.idx_juiz = (self.idx_juiz + 1) % len(self.jogadores)
        self.rodada += 1
        input("\nPressione ENTER para a próxima rodada...")

    def checar_vencedor(self):
        campeoes = [j for j in self.jogadores if j.pontos >= self.meta_pontos]
        if campeoes:
            return max(campeoes, key=lambda x: x.pontos)
        return None

    def iniciar(self):
        while True:
            campeao = self.checar_vencedor()
            if campeao:
                limpar()
                print(f"{C_GREEN}{C_BOLD}" + "=" * 60)
                print(f"   👑 {campeao.nome.upper()} VENCEU O TRIBUNAL DO CAOS! 👑")
                print(f"   Comprovado oficialmente como a mente mais sem escrúpulos da mesa.")
                print("=" * 60 + f"{C_RESET}\n")
                break
            self.executar_rodada()

def configurar():
    limpar()
    print(f"{C_BOLD}{C_MAGENTA}=== ⚖️ TRIBUNAL DO CAOS: GUERRA DE RESPOSTAS ==={C_RESET}\n")
    
    while True:
        qtd_str = input("Quantos amigos na mesa? (3 a 8) [Padrão: 3]: ").strip()
        if not qtd_str:
            qtd = 3
            break
        if qtd_str.isdigit() and 3 <= int(qtd_str) <= 8:
            qtd = int(qtd_str)
            break
        print(f"{C_RED}O jogo brilha com 3 ou mais pessoas!{C_RESET}")

    padroes = ["Major", "Gabriel", "Claudio", "Amigo 4", "Amigo 5", "Amigo 6"]
    nomes = []
    print("\nNomes dos participantes (ENTER para usar o sugerido):")
    for i in range(qtd):
        sugestao = padroes[i] if i < len(padroes) else f"Jogador {i+1}"
        n = input(f"Participante {i+1} [{sugestao}]: ").strip()
        nomes.append(n if n else sugestao)

    meta_str = input("\nQuantos pontos para vencer a partida? [Padrão: 4]: ").strip()
    meta = int(meta_str) if meta_str.isdigit() and int(meta_str) > 0 else 4

    return nomes, meta

if __name__ == "__main__":
    nomes_jogadores, meta_pontos = configurar()
    jogo = JogoTribunal(nomes_jogadores, meta_pontos)
    jogo.iniciar()