import sys
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsProxyWidget, QPushButton
from PySide6.QtMultimedia import *
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Устанавливаем фиксированный размер окна
        self.setFixedSize(805, 605)
        self.show()
class Bird(QGraphicsPixmapItem):
    def __init__(self):  
        super().__init__(QPixmap("bird.png").scaled(50, 50))
        self.setPos(100, 250)
        self.y_velocity = 0
        self.gravity = 1
 
    def jump(self):
        self.y_velocity = -15

    def update_position(self):
        self.y_velocity += self.gravity
        self.setPos(self.x(), self.y() + self.y_velocity)

class Pipe(QGraphicsPixmapItem):
    def __init__(self, top=True):
        super().__init__(QPixmap("pipe.png").scaled(100, 300))
        self.setPos(800, 0 if top else 450)

    def move(self):
        self.setPos(self.x() - 5, self.y())

class RestartMenu(QGraphicsRectItem):
    def __init__(self, scene):
        super().__init__(0, 0, 850, 600)
        self.setBrush(Qt.black)
        self.setOpacity(0.7)

        restart_button = QPushButton("RESTART")
        restart_button.setStyleSheet("background-color:  transparent; border: none;  font: bold italic large  \"Algerian\"; color: red; font-size: 60px;")
        quit_button = QPushButton('QUIT')
        quit_button.setStyleSheet("background-color:  transparent; border: none;  font: bold italic large  \"Algerian\"; color: red; font-size: 60px;")
        proxy = QGraphicsProxyWidget(self)
        proxy1 = QGraphicsProxyWidget(self)
        proxy.setWidget(restart_button)
        proxy1.setWidget(quit_button)
        proxy.setPos(275, 275)
        proxy1.setPos(275, 340)
        scene.addItem(proxy)
        scene.addItem(proxy1)
        restart_button.clicked.connect(scene.reset_game)
        quit_button.clicked.connect(scene.quit_game)  
class GameScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.background = QGraphicsPixmapItem(QPixmap("background.png").scaled(800, 600))
        self.addItem(self.background)

        self.bird = Bird()
        self.addItem(self.bird)

        self.pipes = []
        self.pipe_frame_count = 0  # Counter to track frames between pipes
        self.pipe_spawn_delay = 65  # Number of frames to wait between pipes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(20)

        self.restart_menu = None

        self.setSceneRect(0, 0, 800, 600)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not self.restart_menu:
            self.bird.jump()

    def update_scene(self):
        if not self.restart_menu:
            self.bird.update_position()

            if self.pipe_frame_count == 0:
                pipe_top = Pipe(True)
                pipe_bottom = Pipe(False)
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
                self.show_restart_menu()

            self.pipe_frame_count = (self.pipe_frame_count + 1) % self.pipe_spawn_delay

    def show_restart_menu(self):
        self.restart_menu = RestartMenu(self)

    def reset_game(self):
        self.clear()  # Clear the scene
        self.restart_menu = None
        self.background = QGraphicsPixmapItem(QPixmap("background.png").scaled(800, 600))
        self.addItem(self.background)

        self.bird = Bird()
        self.addItem(self.bird)

        self.pipes = []
        self.pipe_frame_count = 0
        self.setSceneRect(0, 0, 800, 600)
    def quit_game(self):
        sys.exit(app.exec_())


if __name__ == "__main__":
    player = QMediaPlayer()
    audioOutput = QAudioOutput()
    player.setAudioOutput(audioOutput)
    player.setSource(QUrl.fromLocalFile("background_music.mp3"))
    audioOutput.setVolume(50)
    player.play()
    app = QApplication(sys.argv)
    view = QGraphicsView()
    scene = GameScene()
    view.setScene(scene)
    mainw = MyMainWindow()
    
    view.setRenderHint(QPainter.Antialiasing)
    view.setRenderHint(QPainter.SmoothPixmapTransform)

    mainw.setCentralWidget(view)
    sys.exit(app.exec_())
