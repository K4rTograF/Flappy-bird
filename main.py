import sys
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem

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

        self.setSceneRect(0, 0, 800, 600)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.bird.jump()

    def update_scene(self):
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
            sys.exit()

        self.pipe_frame_count = (self.pipe_frame_count + 1) % self.pipe_spawn_delay

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = QGraphicsView()
    scene = GameScene()
    view.setScene(scene)
    view.show()
    sys.exit(app.exec_())   
