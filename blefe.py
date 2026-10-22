import os
import random
import sys
import time

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"

CARTAS_VALIDAS = ["Ás", "Rei", "Dama"]
BARALHO_DIST = ["Ás"] * 8 + ["Rei"] * 8 + ["Dama"] * 8 + ["🃏 Coringa"] * 4

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def pausar(s=1.0):
    time.sleep(s)

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.vidas = 2              # Aguenta 1 tiro, no segundo morre
        self.camaras_revolver = 6   # Roleta Russa: 1 bala real em 6 câmaras
        self.mao = []

    def vivo(self):
        return self.vidas > 0

    def resetar_revolver(self):
        self.camaras_revolver = 6

    def puxar_gatilho(self):
        """Retorna True se disparou (BANG), False se foi clique seco."""
        chance_disparo = 1 / self.camaras_revolver
        disparou = random.random() < chance_disparo

        print(f"\n{C_BOLD}Engatilhando o revólver... ({self.camaras_revolver} câmaras restantes)...{C_RESET}")
        pausar(1.2)
        print(f"{C_RED}{C_BOLD}3...{C_RESET}")
        pausar(0.8)
        print(f"{C_RED}{C_BOLD}2...{C_RESET}")
        pausar(0.8)
        print(f"{C_RED}{C_BOLD}1...{C_RESET}")
        pausar(1.0)

        if disparou:
            print(f"\n{C_RED}{C_BOLD}💥💥💥 BAAAAAAANG! O TIRO DISPAROU! 💥💥💥{C_RESET}")
            self.vidas -= 1
            self.resetar_revolver()
            return True
        else:
            print(f"\n{C_GREEN}{C_BOLD}*CLICK!* ... Câmara vazia! O gatilho estalou no seco!{C_RESET}")
            self.camaras_revolver -= 1  # Fica ainda mais perigoso no próximo tiro
            return False

class JogoLiarsBar:
    def __init__(self, nomes):
        self.jogadores = [Jogador(n) for n in nomes]
        self.idx_atual = 0
        self.carta_mesa = ""
        self.cartas_na_mesa = []     # Pilha com histórico da rodada
        self.ultima_jogada = None    # (jogador, [cartas_reais], qtd_declarada)

    def vivos(self):
        return [j for j in self.jogadores if j.vivo()]

    def proximo_vivo(self):
        while True:
            self.idx_atual = (self.idx_atual + 1) % len(self.jogadores)
            if self.jogadores[self.idx_atual].vivo():
                break

    def mostrar_status(self):
        limpar()
        print(f"{C_BOLD}{C_RED}==================== 🃏 MESA DOS MENTIROSOS 🍺 ===================={C_RESET}")
        print(f"CARTA EXIGIDA NA MESA: {C_YELLOW}{C_BOLD}[ {self.carta_mesa.upper()} ]{C_RESET} (Coringas valem como qualquer carta)")
        print(f"Total acumulado na pilha: {len(self.cartas_na_mesa)} carta(s) viradas")
        print("-------------------------------------------------------------------")
        
        for j in self.jogadores:
            if not j.vivo():
                print(f"💀 {C_RED}{j.nome:<12} | MORTO NA MESA{C_RESET}")
                continue
            
            vidas_str = f"{C_RED}{'♥ ' * j.vidas}{C_RESET}"
            perigo = f"{C_YELLOW}(1 em {j.camaras_revolver} de disparar){C_RESET}"
            cartas_restantes = f"{len(j.mao)} cartas na mão"
            print(f"🤠 {C_BOLD}{j.nome:<12}{C_RESET} | Vidas: {vidas_str:<12} | {cartas_restantes:<18} | Tambor: {perigo}")
        print(f"{C_BOLD}{C_RED}==================================================================={C_RESET}\n")

    def nova_mao(self):
        """Distribui 5 cartas para todos os vivos e sorteia nova carta da mesa."""
        self.carta_mesa = random.choice(CARTAS_VALIDAS)
        self.cartas_na_mesa = []
        self.ultima_jogada = None

        baralho = list(BARALHO_DIST)
        random.shuffle(baralho)

        for j in self.vivos():
            j.mao = [baralho.pop() for _ in range(5)]

    def resolver_desafio(self, acusador):
        autor, cartas_jogadas, qtd = self.ultima_jogada
        limpar()
        self.mostrar_status()
        print(f"🚨 {C_RED}{C_BOLD}{acusador.nome.upper()} GRITOU: 'VOCÊ ESTÁ MENTINDO!'{C_RESET}")
        print(f"{autor.nome} havia jurado que jogou {qtd} carta(s) do tipo {C_YELLOW}[{self.carta_mesa}]{C_RESET}.\n")
        pausar(1.5)

        print(f"Virando as cartas jogadas por {autor.nome}...")
        pausar(1.2)
        cartas_formatadas = " | ".join([f"{C_CYAN}[{c}]{C_RESET}" for c in cartas_jogadas])
        print(f"\nCartas reais na mesa: {cartas_formatadas}\n")
        pausar(1.5)

        # Checa se mentiu: qualquer carta que não seja a exigida e nem coringa é blefe
        mentiu = any(c != self.carta_mesa and c != "🃏 Coringa" for c in cartas_jogadas)

        if mentiu:
            print(f"{C_RED}{C_BOLD}PAGO DE MENTIROSO! {autor.nome} tentou passar a perna na mesa!{C_RESET}")
            print(f"O revólver vai para a cabeça de: {C_RED}{autor.nome}{C_RESET}!")
            pausar(1.5)
            morreu = autor.puxar_gatilho()
            if not autor.vivo():
                print(f"\n💀 {C_RED}{C_BOLD}{autor.nome} PERDEU SUA ÚLTIMA VIDA E FOI ELIMINADO!{C_RESET}")
        else:
            print(f"{C_GREEN}{C_BOLD}FALOU A VERDADE PURA! {autor.nome} realmente jogou o que disse!{C_RESET}")
            print(f"Acusação injusta! O revólver vai para a cabeça de quem duvidou: {C_RED}{acusador.nome}{C_RESET}!")
            pausar(1.5)
            morreu = acusador.puxar_gatilho()
            if not acusador.vivo():
                print(f"\n💀 {C_RED}{C_BOLD}{acusador.nome} PERDEU SUA ÚLTIMA VIDA E FOI ELIMINADO!{C_RESET}")

        pausar(2.5)
        input(f"\n{C_YELLOW}Pressione ENTER para limpar os copos e reiniciar a rodada...{C_RESET}")
        self.nova_mao()

    def jogar_turno(self):
        jogador = self.jogadores[self.idx_atual]
        if not jogador.vivo():
            self.proximo_vivo()
            return

        self.mostrar_status()

        # Se alguém jogou antes, o jogador atual tem a opção de DUVIDAR
        if self.ultima_jogada is not None:
            anterior, _, qtd_ant = self.ultima_jogada
            print(f"O último foi {C_BOLD}{anterior.nome}{C_RESET}, que largou {C_BOLD}{qtd_ant} carta(s){C_RESET} dizendo ser {C_YELLOW}[{self.carta_mesa}]{C_RESET}.")
            print(f"\nVez de: {C_BOLD}{C_CYAN}{jogador.nome}{C_RESET}")
            print(f"[1] 🤫 ACREDITAR (e fazer minha jogada por cima)")
            print(f"[2] 🤬 DUVIDAR ('MENTIROSO! PÕE O REVÓLVER NA MESA!')")

            escolha = ""
            while escolha not in ["1", "2"]:
                escolha = input("\nEscolha sua ação: ").strip()

            if escolha == "2":
                self.resolver_desafio(jogador)
                return

        # Fase de Jogar Cartas
        limpar()
        print(f"\n🔒 {C_YELLOW}Apenas {jogador.nome.upper()} deve olhar a tela agora!{C_RESET}")
        input(f"{jogador.nome}, aperte ENTER quando estiver pronto para ver sua mão...")

        limpar()
        self.mostrar_status()
        print(f"Sua mão secreta, {C_BOLD}{jogador.nome}{C_RESET}:")
        for idx, c in enumerate(jogador.mao, 1):
            print(f"  [{idx}] {c}")

        print(f"\nCarta exigida na mesa: {C_YELLOW}{C_BOLD}[ {self.carta_mesa} ]{C_RESET}")
        print("Quais cartas você quer jogar na mesa viradas para baixo? (De 1 a 3 cartas)")
        print("Exemplo: digite '1' ou '1 3' ou '2 4 5'")

        indices_validos = []
        while not indices_validos:
            entrada = input("\nCartas a jogar: ").strip()
            partes = entrada.replace(",", " ").split()
            nums = [int(p) for p in partes if p.isdigit() and 1 <= int(p) <= len(jogador.mao)]
            nums = list(set(nums))  # Remove duplicados

            if 1 <= len(nums) <= 3:
                indices_validos = sorted(nums, reverse=True)
            else:
                print(f"{C_RED}Você precisa escolher de 1 a 3 cartas válidas da sua mão!{C_RESET}")

        cartas_escolhidas = [jogador.mao.pop(i - 1) for i in indices_validos]
        qtd = len(cartas_escolhidas)
        self.cartas_na_mesa.extend(cartas_escolhidas)
        self.ultima_jogada = (jogador, cartas_escolhidas, qtd)

        limpar()
        print(f"{C_GREEN}✔ Cartas jogadas viradas para baixo na mesa!{C_RESET}")
        input("\nAperte ENTER para liberar a tela para todos...")

        limpar()
        self.mostrar_status()
        print(f"📢 {C_BOLD}{jogador.nome.upper()}{C_RESET} jogou {C_BOLD}{qtd} carta(s){C_RESET} na mesa jurando que são {C_YELLOW}[{self.carta_mesa.upper()}]{C_RESET}!")
        pausar(2.0)

        # Se o jogador esvaziou a mão e ninguém duvidou, ele sobreviveu à rodada
        if len(jogador.mao) == 0:
            print(f"\n🎉 {C_GREEN}{jogador.nome} zerou as cartas da mão com sucesso e venceu a rodada!{C_RESET}")
            pausar(2.0)
            input("\nPressione ENTER para nova rodada...")
            self.nova_mao()

        self.proximo_vivo()

    def iniciar(self):
        self.nova_mao()
        while len(self.vivos()) > 1:
            self.jogar_turno()

        campeao = self.vivos()[0]
        limpar()
        print(f"{C_GREEN}{C_BOLD}" + "=" * 60)
        print(f"       🏆 O ÚLTIMO SOBREVIVENTE DO BAR: {campeao.nome.upper()}! 🏆")
        print("       Todos os outros caíram no blefe ou levaram chumbo!")
        print("=" * 60 + f"{C_RESET}\n")

def configurar():
    limpar()
    print(f"{C_BOLD}{C_RED}=== 🃏 MESA DOS MENTIROSOS: LIAR'S BAR NO TERMINAL ==={C_RESET}\n")
    while True:
        qtd_str = input("Quantos jogadores na mesa? (2 a 6) [Padrão: 3]: ").strip()
        if not qtd_str:
            qtd = 3
            break
        if qtd_str.isdigit() and 2 <= int(qtd_str) <= 6:
            qtd = int(qtd_str)
            break
        print("Digite um número entre 2 e 6.")

    padroes = ["Major", "Gabriel", "Claudio", "Jogador 4", "Jogador 5", "Jogador 6"]
    nomes = []
    print("\nNomes dos jogadores (ENTER para o padrão):")
    for i in range(qtd):
        sugestao = padroes[i] if i < len(padroes) else f"Jogador {i+1}"
        n = input(f"Jogador {i+1} [{sugestao}]: ").strip()
        nomes.append(n if n else sugestao)

    return nomes

if __name__ == "__main__":
    nomes = configurar()
    jogo = JogoLiarsBar(nomes)
    jogo.iniciar()