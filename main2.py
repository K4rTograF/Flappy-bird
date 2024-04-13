import sys
import random
import time
from PySide6.QtCore import Qt, QTimer, QUrl, QPointF
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QApplication,QLabel, QGraphicsScene, QMainWindow, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsProxyWidget, QPushButton
from PySide6.QtMultimedia import *

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Flappy Egypt')
        self.setFixedSize(805, 605)
    
        # player
        self.player = QMediaPlayer()
        self.player.setSource(QUrl.fromLocalFile("background_music.mp3"))
        
        # audio
        self.audioOutput = QAudioOutput()
        self.audioOutput.setVolume(50)
        self.player.setAudioOutput(self.audioOutput)
        self.player.play()
        
        # view
        self.view = QGraphicsView()
        
        # scene
        self.scene = GameScene()
        
        # set scene
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        
        self.setCentralWidget(self.view)


class Bird(QGraphicsPixmapItem):
    def __init__(self):  
        super().__init__(QPixmap("bird.png").scaled(100, 100))
        self.setPos(100, 250)
        self.y_velocity = 0
        self.gravity = -0.8
 
    def jump(self):
        self.y_velocity = 9

    def update_position(self):
        self.y_velocity += self.gravity
        self.setPos(self.x(), self.y() + self.y_velocity)

class Pipe(QGraphicsPixmapItem):
    def __init__(self, height, is_top):
        super().__init__(QPixmap("pipe.png").scaled(100, height))
        if is_top:
            self.setPos(800, -5)
        else:
            self.setPos(800, 600 - height)

    def move(self):
        self.setPos(self.x() - 5, self.y())

class RestartMenu(QGraphicsRectItem):
    def __init__(self, scene):
        super().__init__(0, 0, 850, 600)

        self.scene = scene
        # menu
        restart_button = QPushButton("RESTART")
        quit_button = QPushButton('QUIT')
        restart_info = QLabel('press space to restart game')
        game_status_info = QLabel('Game Over!')
        background_label = QLabel()

        # styles
        game_status_info.setStyleSheet("background-color:  transparent; border: none;  font: bold italic large  \"Algerian\"; color: red; font-size: 60px;")
        restart_info.setStyleSheet("background-color:  transparent; border: none;  font: bold italic large  \"Algerian\"; color: red; font-size: 30px;")
        restart_button.setStyleSheet("background-color:  transparent; border: 2px solid black;  font: bold italic large  \"Algerian\"; color: red; font-size: 50px;")
        quit_button.setStyleSheet("background-color:  transparent; border: none;  font: bold italic large  \"Algerian\"; color: red; font-size: 50px;")
        #proxy_objects
        proxy_restart = QGraphicsProxyWidget(self)
        proxy_quit = QGraphicsProxyWidget(self)
        proxy_label = QGraphicsProxyWidget(self)
        proxy_game_status = QGraphicsProxyWidget(self)

        proxy_restart.setWidget(restart_button)
        proxy_game_status.setWidget(game_status_info)
        proxy_quit.setWidget(quit_button)
        proxy_label.setWidget(restart_info)

        proxy_restart.setPos(280, 275)
        proxy_quit.setPos(280, 340)
        proxy_game_status.setPos(210,150)
        proxy_label.setPos(180,420)

        proxy_restart.setFlag(QGraphicsRectItem.ItemIsFocusable)
        proxy_quit.setFlag(QGraphicsRectItem.ItemIsFocusable)

        scene.addItem(proxy_restart)
        scene.addItem(proxy_game_status)
        scene.addItem(proxy_quit)
        scene.addItem(proxy_label)
        #button_connect
        restart_button.clicked.connect(scene.reset_game)
        quit_button.clicked.connect(scene.quit_game)


class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.background = QGraphicsPixmapItem(QPixmap("background.png").scaled(800, 600))
        self.bird = Bird()

        self.addItem(self.background)
        self.addItem(self.bird)

        self.pipes = []
        self.pipe_frame_count = 0  # Counter to track frames between pipes
        self.pipe_spawn_delay = 70  # Number of frames to wait between pipes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(20)

        self.restart_menu = None

        self.setSceneRect(0, 0, 800, 600)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.restart_menu:
                self.reset_game()
            else:
                self.bird.jump()

    def update_scene(self):
        if not self.restart_menu:
            self.bird.update_position()

            if self.pipe_frame_count == 0:
                # Generate random hole position
                hole_y = random.randint(150, 450)
                # Determine which pipe should be shorter based on hole position
                if hole_y < 300:
                    top_pipe_height = hole_y
                    bottom_pipe_height = 600 - (hole_y + 150)
                else:
                    top_pipe_height = hole_y - 150
                    bottom_pipe_height = 600 - hole_y
                pipe_top = Pipe(top_pipe_height, True)
                pipe_bottom = Pipe(bottom_pipe_height, False)
                self.pipes.extend([pipe_top, pipe_bottom])
                self.addItem(pipe_top)
                self.addItem(pipe_bottom)

            for pipe in self.pipes:
                pipe.move()
                if pipe.x() + pipe.pixmap().width() < 0:
                    self.removeItem(pipe)
                    self.pipes.remove(pipe)

            colliding_items = self.collidingItems(self.bird)
            if any(isinstance(item, Pipe) for item in colliding_items):
                print("Game Over!")
                time.sleep(0.5)
                self.show_restart_menu()
            elif self.bird.pos().y() > 570:
                self.bird.hide()
                time.sleep(0.5)
                self.show_restart_menu()
                print("Game Over!")   
            self.pipe_frame_count = (self.pipe_frame_count + 1) % self.pipe_spawn_delay

    def show_restart_menu(self):
        self.restart_menu = RestartMenu(self)

    def reset_game(self):
        self.clear()  # Clear the scene
        self.restart_menu = None
        self.background  = QGraphicsPixmapItem(QPixmap("background.png").scaled(800, 600))
        self.addItem(self.background)

        self.bird = Bird()
        self.addItem(self.bird)

        self.pipes = []
        self.pipe_frame_count = 0
        self.setSceneRect(0, 0, 800, 600)
    def quit_game(self):
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainw = MyMainWindow()
    mainw.show()
    sys.exit(app.exec_())
