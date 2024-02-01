import eel

from download.download import entry


@eel.expose
def user_input(link: str, path=''):
    entry(link, path)


if __name__ == '__main__':
    # 载入前端
    eel.init('page')
    eel.start('index.html', size=(600, 400), position=(300, 400))
