import pygame
from pygame.locals import *
import random
import math

# Inisialisasi Pygame
pygame.init()

# definisikan warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# view mode
NORMAL_VIEW = "normal_view"
RED_VIEW = "red_view"
GREEN_VIEW = "green_view"

view_mode = NORMAL_VIEW

# hitung waktu gerak
last_move = pygame.time.get_ticks()

# path droids
red_droids_paths = []
green_droid_paths = []

# array droids
green_droid = []
red_droids = []

is_running:bool = False
is_first:bool = False
is_stopped:bool = False

# radius penglihatan green droid
radius = 7

# ubah setiap tepi jadi dinding
def create_border(maze):
    new_maze = maze.copy()  # Membuat salinan peta agar peta awal tetap tidak berubah

    # Mendapatkan jumlah baris dan kolom pada peta
    baris = len(maze)
    kolom = len(maze[0])

    for i in range(baris):
        for j in range(kolom):
            if i == 0 or i == baris - 1 or j == 0 or j == kolom - 1:
                new_maze[i][j] = 0
    return new_maze

# fungsi untuk mendefinisikan map yg terhubung jalan dg backtracking
def generate_maze(width, height):
    # Membuat peta dengan seluruh tembok
    maze = [[0] * width for _ in range(height)]

    # Posisi awal dan akhir jalan
    start_x, start_y = random.randint(0, width-1), random.randint(0, height-1)
    end_x, end_y = random.randint(0, width-1), random.randint(0, height-1)

    # Fungsi backtracking untuk membuat jalan
    def backtrack(x, y):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        # mencoba setiap arah pergerakan
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 0:
                maze[y + dy // 2][x + dx // 2] = 1
                maze[ny][nx] = 1
                backtrack(nx, ny)

    # Menandai posisi awal dan akhir jalan
    maze[start_y][start_x] = 2
    maze[end_y][end_x] = 3

    # Memulai pembuatan jalan dari posisi awal
    backtrack(start_x, start_y)

    return (maze)

# Grid peta
map = generate_maze(50,50)
print(map)

# ukuran grid
grid_size = 14
# Menghitung jumlah grid
rows = len(map)
columns = len(map[0])

# Lebar dan tinggi jendela sesuai dengan grid
window_width = columns * grid_size
window_height = rows * grid_size

# Membuat jendela Pygame
screen = pygame.display.set_mode((window_width + 220, window_height+20))
pygame.display.set_caption('Hide and Seek')
# Inisialisasi font teks
font = pygame.font.SysFont(None, 17)
screen.fill(WHITE)

def get_button_pos(height):

    # Inisialisasi posisi dan ukuran tombol
    button_width, button_height = 190, 50
    button_x = (window_width + button_width)
    button_y = (height - 50)

    output = {
        "button_width" : button_width,
        "button_height" : button_height,
        "button_x" : 0,
        "button_y" : button_y,
        }

    return output

# Fungsi untuk menampilkan teks di tengah tombol
def display_text(text, btn_height):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=( 95, (btn_height)+25))
    screen.blit(text_surface, text_rect)

def add_green_droid():
    green_droid.clear()
    is_on_path = False
    i = random.randint(0, 49)
    j = random.randint(0, 49)
    while not is_on_path:
        if map[i][j] == 1:
           
            if red_droids:
                if [i,j] not in red_droids:
                    green_droid.append(i)
                    green_droid.append(j)
                    is_on_path = True
                else:
                    i = random.randint(0, 49)
                    j = random.randint(0, 49)
                
            else:
                green_droid.append(i)
                green_droid.append(j)
                is_on_path = True
        else:
            i = random.randint(0, 49)
            j = random.randint(0, 49)

def add_red_droid():
    is_on_path = False
    i = random.randint(0, 49)
    j = random.randint(0, 49)
    while not is_on_path:
        if map[i][j] == 1:
            # cek jangan sama dengan greendroid
            if green_droid:
                if(i!= green_droid[0] and j != green_droid[1]):
                    red_droids.append([i, j])
                    is_on_path = True
                else:
                    i = random.randint(0, 49)
                    j = random.randint(0, 49)

            else:
                red_droids.append([i, j])
                is_on_path = True
        else:
            i = random.randint(0, 49)
            j = random.randint(0, 49)

def shuffle_red_droid():
    droid_count = len(red_droids)
    red_droids.clear()
    for i in range(droid_count):
        add_red_droid() 

def get_viewable_map():
    # Mendapatkan posisi droid hijau
    green_x, green_y = green_droid[1], green_droid[0]

    # Mendapatkan batas atas, bawah, kiri, dan kanan yang terlihat oleh droid hijau
    radius = 5  # Jarak pandang droid hijau
    top = max(0, green_x - radius)
    bottom = min(len(map), green_x + radius + 1)
    left = max(0, green_y - radius)
    right = min(len(map[0]), green_y + radius + 1)

    # Mengembalikan peta yang hanya menampilkan daerah yang terlihat oleh droid hijau
    viewable_map = []
    for row in range(top, bottom):
        visible_row = []
        for column in range(left, right):
            visible_row.append(map[row][column])
        viewable_map.append(visible_row)

    return viewable_map

# Fungsi untuk menggambar peta
def draw_map():

    map_surface = pygame.Surface((window_width, window_height))
    for row in range(rows):
        for column in range(columns):
            if map[row][column] == 0:  # Tembok
                pygame.draw.rect(map_surface, (0, 0, 0), ((column * grid_size) + 0 , row * grid_size, grid_size, grid_size))
            elif map[row][column] == 1:  # Jalan
                pygame.draw.rect(map_surface, (255, 255, 255), ((column * grid_size) + 0, row * grid_size, grid_size, grid_size))

            if view_mode == GREEN_VIEW:
                viewable_map = get_viewable_map()
                for row in range(len(viewable_map)):
                    for column in range(len(viewable_map[0])):
                        if viewable_map[row][column] == 0:  # Tembok
                            pygame.draw.rect(map_surface, (0, 0, 0), ((column * grid_size) + 0, row * grid_size, grid_size, grid_size))
                        elif viewable_map[row][column] == 1:  # Jalan
                            pygame.draw.rect(map_surface, (255, 255, 255), ((column * grid_size) + 0, row * grid_size, grid_size, grid_size))
                        else:
                            # Mendapatkan posisi droid hijau
                            green_x, green_y = green_droid[1], green_droid[0]

                            # Mendapatkan batas atas, bawah, kiri, dan kanan yang terlihat oleh droid hijau
                            radius = 2  # Jarak pandang droid hijau
                            top = max(0, green_x - radius)
                            bottom = min(len(map), green_x + radius + 1)
                            left = max(0, green_y - radius)
                            right = min(len(map[0]), green_y + radius + 1)

                            # Menggambar peta yang berada di sekitar droid hijau
                            for row in range(top, bottom):
                                for column in range(left, right):
                                    if map[row][column] == 0:  # Tembok
                                        pygame.draw.rect(map_surface, (0, 0, 0), ((column * grid_size) + 0, row * grid_size, grid_size, grid_size))
                                    elif map[row][column] == 1:  # Jalan
                                        pygame.draw.rect(map_surface, (255, 255, 255), ((column * grid_size) + 0, row * grid_size, grid_size, grid_size))

    # cek apa greendroids sudah ditambahkan
    if green_droid:
        center = ((green_droid[1] * grid_size)+7,(green_droid[0] * grid_size)+7)
        pygame.draw.circle(map_surface, GREEN, center  , 7)
    
    # cek apa reddroids sudah ditambahkan
    if red_droids:
        for droid in red_droids:
            center = ((droid[1] * grid_size)+7,(droid[0] * grid_size)+7)
            pygame.draw.circle(map_surface, RED, center  , 7)

    screen.blit(map_surface, (200, 0))

def button_view_droid_hijau():
    global view_mode
    if view_mode == NORMAL_VIEW:
        view_mode = GREEN_VIEW
        draw_map()  # Memanggil fungsi draw_map() untuk menggambar peta dengan view_mode baru
    else:
        view_mode = NORMAL_VIEW
        draw_map()  # Memanggil fungsi draw_map() untuk menggambar peta dengan view_mode baru


def is_valid_move(x, y):
    # Memeriksa apakah langkah ke (x, y) adalah langkah yang valid
    rows = len(map)
    cols = len(map[0])
    if x >= 0 and x < rows and y >= 0 and y < cols and map[x][y] == 1:
        return True
    return False

from collections import deque
def bfs_seek(start, end):
    rows = len(map)
    cols = len(map[0])
    visited = [[False] * cols for _ in range(rows)]  # Menandai apakah suatu posisi telah dikunjungi
    prev = [[None] * cols for _ in range(rows)]  # Menyimpan posisi sebelumnya untuk mencari jalur tercepat
    queue = deque([start])  # Antrian untuk menjelajahi posisi secara BFS

    # Gerakan ke 4 arah: atas, kanan, bawah, kiri
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    while queue:
        x, y = queue.popleft()  # Mengambil posisi pertama dari antrian

        if (x, y) == end:
            # Jalur tercepat telah ditemukan, membangun jalur dari akhir ke awal
            path = []
            curr = end
            while curr != start:
                path.append(curr)
                curr = prev[curr[0]][curr[1]]
            path.append(start)
            path.reverse()
            return path

        if not visited[x][y]:
            visited[x][y] = True

            # Mengeksplorasi gerakan ke 4 arah yang mungkin
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if is_valid_move(new_x, new_y) and not visited[new_x][new_y]:
                    queue.append((new_x, new_y))
                    prev[new_x][new_y] = (x, y)

    return None  # Tidak ada jalur yang bisa dilewati

def check_enemy():
    x1, y1 = green_droid[0], green_droid[1]
    for point in red_droids:
        x2, y2 = point
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distance <= radius:
            return False
    return True

# cek apakah yg dilalui green droid aman dari jarak radius lintasan red droid
def is_dangerous(pos:list[int]):
    for red_path in red_droids_paths:
        if len(red_path)<=radius:
            for red_pos in red_path:
                if pos[0] == red_pos[0] and pos[1] == red_pos[1]:
                    return True
    return False

def find_random_point():
    rows = len(map)
    cols = len(map[0])
    while True:
        random_x = random.randint(0, rows - 1)
        random_y = random.randint(0, cols - 1)
        if map[random_x][random_y] == 1:
            return (random_x, random_y)

def create_path(A):
    random_point = find_random_point(map)
    print("Titik acak yang dipilih:", random_point)

    path = bfs_seek(A, random_point)
    if path is None:
        for pos in path:
            print(pos)

def is_catched():
    
    for droid in red_droids:
        x =  droid[0]
        y = droid[1]
        if green_droid and x == green_droid[0] and y == green_droid[1]:
            return True
    False

SAFE_DISTANCE = 10  # Ganti dengan nilai jarak yang diinginkan

def move_red_droids():
    global is_first
    global is_stopped
    if is_catched():
        is_stopped = True
    if is_first:
        for droid in red_droids:
            start = (droid[0], droid[1])
            end = (green_droid[0], green_droid[1])  # Titik tujuan
            path = bfs_seek(start, end)
            path.pop(0)
            red_droids_paths.append(path)

    for i, droid in enumerate(red_droids):
        if len(red_droids_paths[i]) > 0:
            # new x and y
            (x, y) = red_droids_paths[i][0]

            if is_catched():
                move_away_from_red_droid()
            else:
                red_droids[i][0] = x
                red_droids[i][1] = y
                red_droids_paths[i].pop(0)
        else:
            start = (droid[0], droid[1])
            end = (green_droid[0], green_droid[1]) 
            path = bfs_seek(start, end)
            path.pop(0)
            red_droids_paths[i] = path
            (x, y) = red_droids_paths[i][0]
            if is_catched():
                move_away_from_red_droid()
            else:
                red_droids[i][0] = x
                red_droids[i][1] = y
                red_droids_paths[i].pop(0)

    if is_catched():
        is_stopped = True

def move_green_droid():
    global is_stopped
    if is_catched():
        is_stopped = True

    is_safe = check_enemy()

    if not is_safe:
        global is_first
        global green_droid_paths
        if is_first:
            random_point = find_random_point()
            print(f"start {green_droid}, end : {random_point}")
            start = (green_droid[0], green_droid[1])  # Titik tujuan
            path = bfs_seek(start, random_point)
            print(path)
            path.pop(0)
            green_droid_paths = path

        if len(green_droid_paths) > 0:
            (x, y) = green_droid_paths[0]
            dx = x - green_droid[0]
            dy = y - green_droid[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Periksa apakah droid merah berada dalam jarak aman, jika ya, maka hindari
            if distance > SAFE_DISTANCE:
                move_away_from_red_droid()
            else:
                # Pergerakan normal jika jarak droid merah aman
                green_droid[0] = x
                green_droid[1] = y
                green_droid_paths.pop(0)
        else:
            random_point = find_random_point()
            print(f"start {green_droid}, end : {random_point}")
            start = (green_droid[0], green_droid[1])  # Titik tujuan
            path = bfs_seek(start, random_point)
            print(path)
            path.pop(0)
            green_droid_paths = path
            (x, y) = green_droid_paths[0]
            green_droid[0] = x
            green_droid[1] = y
            green_droid_paths.pop(0)

    if is_catched():
        is_stopped = True

def move_away_from_red_droid():
    global green_droid
    global green_droid_paths

    # Memeriksa apakah terdapat jalur yang telah ditentukan untuk droid hijau
    if len(green_droid_paths) > 0:
        (x, y) = green_droid_paths[0]
        dx = green_droid[0] - x
        dy = green_droid[1] - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < SAFE_DISTANCE:
            green_droid[0] = x
            green_droid[1] = y
            green_droid_paths.pop(0)
        else:
            start = (green_droid[0], green_droid[1])
            end = (x, y)
            path = bfs_seek(start, end)
            path.pop(0)
            green_droid_paths = path
            (x, y) = green_droid_paths[0]
            green_droid[0] = x
            green_droid[1] = y
            green_droid_paths.pop(0)
    else:
        random_point = find_random_point()
        print(f"start {green_droid}, end : {random_point}")
        start = (green_droid[0], green_droid[1])
        path = bfs_seek(start, random_point)
        print(path)
        path.pop(0)
        green_droid_paths = path
        (x, y) = green_droid_paths[0]
        green_droid[0] = x
        green_droid[1] = y
        green_droid_paths.pop(0)

# Loop utama
running = True
while running:
    if is_catched():
        is_stopped = True

    screen.fill((0, 0, 0))  # Bersihkan layar dengan warna hitam

    #cek apakah game berjalan atau dijeda
    # print(radius)
    if is_stopped:
        # Membuat  game over
            btn_prop = get_button_pos(500)
            btn_notif= pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
            pygame.draw.rect(screen, (255, 0, 0), btn_notif)
            display_text("GAME OVER", btn_prop["button_y"])
    if is_running and not is_stopped:
        if(red_droids and green_droid):
           
            # print("played")
            # Mendapatkan waktu sekarang
            current_time = pygame.time.get_ticks()
            # Memeriksa apakah sudah melewati 0,5 detik sejak gerakan terakhir
            if current_time - last_move >= 100:
                last_move = current_time  # Memperbarui waktu gerakan terakhir
                move_green_droid()
                move_red_droids()
                is_first = False 

            if is_catched():
                is_stopped = True
    draw_map()
   
    # Membuat  tombol play
    btn_prop = get_button_pos(55)
    btn_play = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"], btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_play)
    display_text("PLAY", btn_prop["button_y"])

    # Membuat  tombol shuffle
    btn_prop = get_button_pos(110)
    btn_shuffle = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_shuffle)
    display_text("ACAK MAP", btn_prop["button_y"])

    # Membuat  tombol add greendroid
    btn_prop = get_button_pos(165)
    btn_add_green_droid = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_add_green_droid)
    display_text("TAMBAH/ACAK DROID HIJAU", btn_prop["button_y"])

    # Membuat  tombol add reddroid
    btn_prop = get_button_pos(220)
    btn_add_red_droid = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_add_red_droid)
    display_text("TAMBAH DROID MERAH", btn_prop["button_y"])

    # Membuat  tombol ashuffke reddroid
    btn_prop = get_button_pos(275)
    btn_shuffle_red_droid = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_shuffle_red_droid)
    display_text("ACAK DROID MERAH", btn_prop["button_y"])

    # Membuat  tombol view greendroid
    btn_prop = get_button_pos(330)
    btn_view_green_droid = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_view_green_droid)
    display_text("VIEW DROID HIJAU ", btn_prop["button_y"])

    #Membuat  tombol view reddroid
    btn_prop = get_button_pos(385)
    btn_view_red_droid = pygame.Rect(btn_prop["button_x"], btn_prop["button_y"] , btn_prop["button_width"], btn_prop["button_height"])
    pygame.draw.rect(screen, (0, 0, 255), btn_view_red_droid)
    display_text("VIEW DROID MERAH", btn_prop["button_y"])
    
    # Mendapatkan posisi mouse
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN: 

            if not is_running and not is_stopped:
                if btn_shuffle.collidepoint(mouse_pos):
                            
                    map = generate_maze(50,50)

                    # reset semua droids
                    green_droid.clear()
                    red_droids.clear()

                elif btn_add_green_droid.collidepoint(mouse_pos):
                    add_green_droid()
                elif btn_add_red_droid.collidepoint(mouse_pos):
                    add_red_droid()
                elif btn_shuffle_red_droid.collidepoint(mouse_pos):
                    shuffle_red_droid()
                elif btn_play.collidepoint(mouse_pos):
                
                    is_running = True
                    is_first = True
                    
            if btn_view_green_droid.collidepoint(mouse_pos):
                    print(f"changed to {view_mode}")
                    if green_droid:
                        if(view_mode == GREEN_VIEW):
                            view_mode = NORMAL_VIEW
                        else:
                            view_mode = GREEN_VIEW
                            print(f"changed to {view_mode}")
      
    # Menggambar peta
    pygame.display.flip()
