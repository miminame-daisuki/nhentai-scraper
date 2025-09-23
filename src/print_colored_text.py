class bcolors:
    HEADER = '\033[95m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


if __name__ == '__main__':
    print(f'{bcolors.HEADER}Hello world{bcolors.ENDC}')
