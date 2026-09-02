from kivy.animation import Animation


def fade_in(widget, duration=0.18):
    Animation.cancel_all(widget)
    widget.opacity = 0
    Animation(opacity=1, duration=duration, transition="out_quad").start(widget)


def pulse(widget):
    Animation.cancel_all(widget)
    base = widget.opacity
    (
        Animation(opacity=0.65, duration=0.07)
        + Animation(opacity=base, duration=0.11)
    ).start(widget)
