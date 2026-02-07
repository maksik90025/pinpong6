from pygame import *
import socket
import json
from threading import Thread

# --- НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
mixer.init()

screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- ФОН ---
bg = transform.scale(
    image.load("maksim.png").convert(),
    (WIDTH, HEIGHT)
)

# --- СПРАЙТИ ---
paddle_img = transform.scale(
    image.load("./images.jfif54-removebg-preview.png").convert_alpha(), (20, 100)
)

ball_img = transform.scale(
    image.load("./Ball_nast_ten_Atemi_3-min-removebg-preview.png").convert_alpha(), (20, 20)
)

# --- ЗВУКИ ---




# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            break


# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ГРА ---
game_over = False
you_winner = None
played_win_sound = False

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            quit()

    # --- ВІДЛІК ---
    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.blit(bg, (0, 0))
        text = font_win.render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        display.update()
        continue

    # --- ПЕРЕМОГА ---
    if "winner" in game_state and game_state["winner"] is not None:
        screen.blit(bg, (0, 0))

        if not played_win_sound:
            win_sound.play()
            played_win_sound = True

        text = "Ти переміг!" if game_state["winner"] == my_id else "Ти програв"
        win_text = font_win.render(text, True, (255, 215, 0))
        screen.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        display.update()
        continue

    # --- ГРА ---
    if game_state:
        screen.blit(bg, (0, 0))

        screen.blit(paddle_img, (20, game_state['paddles'][0]))
        screen.blit(paddle_img, (WIDTH - 40, game_state['paddles'][1]))
        screen.blit(ball_img, (game_state['ball']['x'] - 10, game_state['ball']['y'] - 10))

        score = font_main.render(
            f"{game_state['scores'][0]} : {game_state['scores'][1]}",
            True, (255, 255, 255)
        )
        screen.blit(score, (WIDTH // 2 - 25, 20))

        if game_state['sound_event'] == 'wall_hit':
            wall_hit_sound.play()
        elif game_state['sound_event'] == 'platform_hit':
            platform_hit_sound.play()

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")