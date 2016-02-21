from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle
from random import randint

from kivy.config import Config

Config.set('graphics', 'resizeable', 0)
Window.clearcolor = (0, 0, 0, 1.)


class WidgetDrawer(Widget):
    # draw all widgets on screen
    # set positions and background collision boxes

    def __init__(self, image_str, **kwargs):
        super(WidgetDrawer, self).__init__(**kwargs)
        with self.canvas:
            self.size = (Window.width * .002 * 25, Window.width * .002 * 25)
            self.rect_bg = Rectangle(
                    source=image_str, pos=self.pos, size=self.size)
            # update graphics when position moves
            self.bind(pos=self.update_graphics_pos)
            self.x = self.center_x
            self.y = self.center_y
            self.pos = (self.x, self.y)
            # centre collision rectangle on image
            self.rect_bg.pos = self.pos

    def update_graphics_pos(self, instance, value):
        # if image moves, collision rectangle moves
        self.rect_bg.pos = value

    def set_size(self, width, height):
        # widget size
        self.size = (width, height)

    def set_pos(self, xpos, ypos):
        # widget position
        self.x = xpos
        self.y = ypos


class Pickard(WidgetDrawer):
    # dodge Pickard's head
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y

    def update(self):
        self.move()


class Shatner(WidgetDrawer):
    # control shatner's head
    impulse = 3  # move up speed
    grav = -0.1  # move down speed

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # stop rising too much
        if self.y == Window.height * 0.95:
            self.impulse = -3

    def determine_velocity(self):
        # gravity speed increases as you fall
        self.grav *= 1.05
        # set terminal velocity
        if self.grav < 4:
            self.grav = -4

        # y position is combo of tapped up thrust
        # and simulated gravity
        self.velocity_y = self.impulse + self.grav
        # upward velocity decay
        self.impulse *= 0.95

    def update(self):
        self.determine_velocity()
        self.move()


class MyButton(Button):
    # button to tap
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.font_size = Window.width * 0.018


class GUI(Widget):
    # main screen container for the game play
    pickardList = []
    minProb = 1700  # Pickard Spawn rate

    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        # title name
        l = Label(text='Flappy Shatner')
        # title positioning
        l.x = (Window.width / 2) - (l.width / 2)
        l.y = Window.height * 0.8
        # apply
        self.add_widget(l)

        # create shatner's head and centre
        self.shatner = Shatner(image_str='‪/images/main.png')
        self.shatner.x = Window.width / 4
        self.shatner.y = Window.height / 2
        self.add_widget(self.shatner)

    def add_pickard(self):
        # adding the heads to the screen
        image_number = randint(1, 4)
        image_str = '/images/avoid/Pickard{}.png'.format(image_number)
        tmp_pickard = Pickard(image_str)
        tmp_pickard.x = Window.width * 0.99

        # randomising the y position
        ypos = randint(1, 4)
        ypos = ypos * Window.height * .0625

        tmp_pickard.y = ypos
        tmp_pickard.velocity_y = 0
        vel = 10
        tmp_pickard.velocity_x = -0.1 * vel

        self.pickardList.append(tmp_pickard)
        self.add_widget(tmp_pickard)

    # input handling
    def on_touch_down(self, td):
        self.shatner.impulse = 3
        self.shatner.grav = -0.1

    def game_over(self):
        restart_button = MyButton(text='Restart')

        def restart_button():
            # print 'restart button pressed'
            # reset game
            for k in self.pickardList:
                self.remove_widget(k)
                self.shatner.xpos = Window.width * 0.25
                self.shatner.ypos = Window.height * 0.5
                self.minProb = 1700

            self.pickardList = []

            self.parent.remove_widget(restart_button)

            # restart Game clock
            Clock.unschedule(self.update)
            Clock.schedule_interval(self.update, 1.0 / 60.0)

            restart_button.size = (Window.width * .3, Window.width * .1)
            restart_button.pos = (Window.width * 0.5) - \
                                 (restart_button.width / 2), \
                                 Window.height * 0.5
            # only call when button is released
            restart_button.bind(on_release=restart_button)

    def update(self, dt):
        # game update function
        self.shatner.update()
        # randomly add Pickard heads
        tmp_count = randint(1, 1800)
        if tmp_count > self.minProb:
            self.add_pickard()
            if self.minProb < 1300:
                self.minProb = 1300
            self.minProb -= 1

        for k in self.pickardList:
            # check for collision with pickard head
            if k.collide_widget(self.shatner):
                self.game_over()
                Clock.unschedule(self.update)
            k.update()


class ClientApp(App):

    def build(self):
        parent = Widget()
        app = GUI()
        # game clock
        Clock.schedule_interval(app.update, 1.0 / 60.0)
        parent.add_widget(app)
        return parent


if __name__ == '__main__':
    ClientApp().run()
