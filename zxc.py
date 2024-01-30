from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtCore import QRect, QPropertyAnimation

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 400, 300)  # Установите геометрию окна
        self.setWindowTitle('Widget Animation Example')

        # Создайте кнопку и установите обработчик событий
        self.button = QPushButton('Animate', self)
        self.button.clicked.connect(self.startAnimation)

        # Создайте прямоугольник, представляющий объект в окне
        self.object_width = 30
        self.object_height = 30
        self.object_x = 50
        self.object_y = 50

    def startAnimation(self):
        # Создайте объект анимации для изменения свойства "geometry"
        animation = QPropertyAnimation(self, b"geometry")
        # Установите начальное и конечное значения геометрии (пример)
        start_rect = QRect(self.object_x, self.object_y, self.object_width, self.object_height)
        end_rect = QRect(200, 200, self.object_width, self.object_height)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        # Установите длительность анимации в миллисекундах
        animation.setDuration(1000)  # 1 секунда
        # Запустите анимацию
        animation.start()

if __name__ == "__main__":
    app = QApplication([])

    widget = MyWidget()
    widget.show()

    app.exec()
