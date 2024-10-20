import sys
import random
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPixmap, QPainter, QFont, QBrush, QColor
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsScene, QMainWindow, QGraphicsView, QGraphicsTextItem, \
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsProxyWidget, QPushButton
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

GRAVITY = -0.8  


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Летучий Египет')
        self.setFixedSize(805, 605)

        self.view = QGraphicsView()
        self.start_scene = StartScene(self)  

        self.view.setScene(self.start_scene) 
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setCentralWidget(self.view)

    def show_start_screen(self):
        self.view.setScene(self.start_scene)

    def start_game(self):
        self.game_scene = GameScene(self)  
        self.view.setScene(self.game_scene)  
        self.game_scene.start_game()

    def close(self):
        sys.exit(app.exec())

class StartScene(QGraphicsScene):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setSceneRect(0, 0, 800, 600)

        self.background = QGraphicsPixmapItem(QPixmap("start_background.png").scaled(800, 600))
        self.addItem(self.background)

        title = QGraphicsTextItem("Летучий Египет")
        title.setDefaultTextColor(Qt.red)
        title.setFont(QFont("Algerian", 50))
        title.setPos(150, 100)
        self.addItem(title)

        start_button = QPushButton("НАЧАТЬ")
        start_button.setStyleSheet(
            "background-color: transparent; border: 2px solid black; font: bold italic large 'Algerian'; color: red; font-size: 50px;")
        proxy_start = QGraphicsProxyWidget()
        proxy_start.setWidget(start_button)
        proxy_start.setPos(280, 275)
        self.addItem(proxy_start)

        start_button.clicked.connect(self.main_window.start_game)

        quitt_button = QPushButton("ВЫХОД")
        quitt_button.setStyleSheet(
            "background-color: transparent; border: 2px solid black; font: bold italic large 'Algerian'; color: red; font-size: 50px;")
        proxy_quit = QGraphicsProxyWidget()
        proxy_quit.setWidget(quitt_button)
        proxy_quit.setPos(280, 375)
        self.addItem(proxy_quit)

        quitt_button.clicked.connect(self.main_window.close)



class Bird(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__(QPixmap("bird2.png").scaled(70, 50))
        self.setPos(100, 250)
        self.y_velocity = 0

    def jump(self):
        global GRAVITY
        if GRAVITY < 0:  
            self.y_velocity = 9
        else:  
            self.y_velocity = -9

    def update_position(self):
        self.y_velocity += GRAVITY  
        self.setPos(self.x(), self.y() + self.y_velocity)


class Pipe(QGraphicsPixmapItem):
    def __init__(self, height, is_top):
        super().__init__(QPixmap("pipe.png").scaled(100, height))
        self.passed = False
        if is_top:
            self.setPos(800, -5)
        else:
            self.setPos(800, 600 - height)

    def move(self):
        self.setPos(self.x() - 5, self.y())

class Spike(QGraphicsPixmapItem):
    def __init__(self, y_position):
        super().__init__(QPixmap("spike.png").scaled(50, 50))
        self.setPos(800, y_position)
        self.gravity_toggled = False

    def move(self):
        self.setPos(self.x() - 10, self.y())

class RestartMenu(QGraphicsRectItem):
    def __init__(self, scene):
        super().__init__(0, 0, 610, 400)

        self.scene = scene

        self.setPos((850 - 650) / 2, (600 - 400) / 2)
        self.setBrush(QBrush(QColor(255, 255, 204, 150)))  

        restart_button = QPushButton("")
        quit_button = QPushButton('Выйти в главное меню')
        restart_info = QLabel('Нажмите Enter, чтобы начать заново ')
        game_status_info = QLabel('Игра окончена!')

        # Styles
        game_status_info.setStyleSheet(
            "background-color: transparent; border: none; font: bold italic large 'Algerian'; color: red; font-size: 60px;")
        restart_info.setStyleSheet(
            "background-color: transparent; border: none; font: bold italic large 'Algerian'; color: red; font-size: 30px;")
        restart_button.setStyleSheet(
            "background-color: transparent; border: none; font: bold italic large 'Algerian'; color: red; font-size: 1px;")
        quit_button.setStyleSheet(
            "background-color: transparent; border: 2px solid yellow; font: bold italic large 'Algerian'; color: red; font-size: 50px;")

        # Proxy widgets
        proxy_restart = QGraphicsProxyWidget(self)
        proxy_quit = QGraphicsProxyWidget(self)
        proxy_label = QGraphicsProxyWidget(self)
        proxy_game_status = QGraphicsProxyWidget(self)

        proxy_restart.setWidget(restart_button)
        proxy_game_status.setWidget(game_status_info)
        proxy_quit.setWidget(quit_button)
        proxy_label.setWidget(restart_info)

        proxy_restart.setPos(350, 200)
        proxy_quit.setPos(1, 160)
        proxy_game_status.setPos(60, 30)
        proxy_label.setPos(10, 260)

        proxy_restart.setFlag(QGraphicsRectItem.ItemIsFocusable)
        proxy_quit.setFlag(QGraphicsRectItem.ItemIsFocusable)

        scene.addItem(self)
        scene.addItem(proxy_restart)
        scene.addItem(proxy_game_status)
        scene.addItem(proxy_quit)
        scene.addItem(proxy_label)

        # Button connections
        restart_button.clicked.connect(self.scene.reset_game)
        quit_button.clicked.connect(self.scene.quit_game)





class GameScene(QGraphicsScene):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initialize_game()


    def initialize_game(self):
        self.background = QGraphicsPixmapItem(QPixmap("background.png").scaled(800, 600))
        self.bird = Bird()

        self.addItem(self.background)
        self.addItem(self.bird)

        self.pipes = []
        self.pipe_frame_count = 0
        self.pipe_spawn_delay = 100

        self.spikes = []  
        self.spike_frame_count = 0 
        self.spike_on_screen = False 
        self.spike_spawn_delay = random.randint(10, 20)  #delay for spikes

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)

        self.restart_menu = None
        self.setSceneRect(0, 0, 800, 600)

        self.score = 0
        self.score_display = QGraphicsTextItem()
        self.score_display.setPlainText(f"СЧЁТ: {self.score}")
        self.score_display.setDefaultTextColor(Qt.red)
        self.score_display.setFont(QFont('Algerian', 25))
        self.score_display.setPos(335, 10)
        self.addItem(self.score_display)

        self.player = QMediaPlayer()
        self.player.setSource(QUrl.fromLocalFile("background_music.mp3"))
        self.audioOutput = QAudioOutput()
        self.audioOutput.setVolume(50)
        self.player.setAudioOutput(self.audioOutput)
        self.player.setLoops(QMediaPlayer.Infinite)
        self.player.play()

    def start_game(self):
        self.timer.start(20) 

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.bird.jump()
        if event.key() == Qt.Key_Return:
            if self.restart_menu:
                self.reset_game()

    def update_scene(self):
        global GRAVITY

        if not self.restart_menu:
            self.bird.update_position()

            # PIPE SPAWNING LOGIC
            if self.pipe_frame_count == 0:
                hole_y = random.randint(150, 450)
                top_pipe_height = hole_y if hole_y < 300 else hole_y - 150
                bottom_pipe_height = 600 - (hole_y + 150) if hole_y < 300 else 600 - hole_y

                pipe_top = Pipe(top_pipe_height, True)
                pipe_bottom = Pipe(bottom_pipe_height, False)
                self.pipes.extend([pipe_top, pipe_bottom])
                self.addItem(pipe_top)
                self.addItem(pipe_bottom)

            # SPIKE SPAWNING LOGIC
            if self.spike_frame_count == 0 and not self.spike_on_screen:
                spike_y = random.randint(150, 450)  #between pipes
                spike = Spike(spike_y)
                self.addItem(spike)
                self.spikes.append(spike) 
                self.spike_on_screen = True 

            for spike in self.spikes[:]:  
                spike.move()
                if spike.x() + spike.pixmap().width() < 0:  #offscreen
                    self.removeItem(spike)  
                    self.spikes.remove(spike)  
                    self.spike_on_screen = False

            for pipe in self.pipes:
                pipe.move()
                if not pipe.passed and pipe.x() + pipe.pixmap().width() < self.bird.x():
                    pipe.passed = True
                    self.score += 0.5

            self.pipes = [pipe for pipe in self.pipes if pipe.x() + pipe.pixmap().width() > 0]


            self.score_display.setPlainText(f"СЧЁТ: {int(self.score)}")

            #collisions
            colliding_items = self.collidingItems(self.bird)
            if any(isinstance(item, Pipe) for item in
                   colliding_items) or self.bird.pos().y() > 570 or self.bird.pos().y() < 0:
                print("Game Over!")
                self.show_restart_menu()
                self.player.stop()

            if any(isinstance(item, Spike) for item in colliding_items):
                for item in colliding_items:
                    if isinstance(item,Spike) and not item.gravity_toggled:
                        GRAVITY = -GRAVITY 
                        item.gravity_toggled = True

            self.pipe_frame_count = (self.pipe_frame_count + 1) % self.pipe_spawn_delay # Pipe delay logic
            self.spike_frame_count = (self.spike_frame_count + 1) % self.spike_spawn_delay  # Spike delay logic

    def show_restart_menu(self):
        self.restart_menu = RestartMenu(self)

    def reset_game(self):
        global GRAVITY
        GRAVITY = -0.8
        if self.restart_menu:
            self.timer.stop()
            self.clear()
            self.initialize_game()
            self.timer.start(20)

    def quit_game(self):
        self.timer.stop()
        self.clear()
        self.main_window.show_start_screen()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainw = MyMainWindow()
    mainw.show()
    sys.exit(app.exec())
