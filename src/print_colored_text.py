class bcolors:
    HEADER = '\033[95m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


if __name__ == '__main__':
    print(f'{bcolors.HEADER}Header{bcolors.ENDC}')
    print(f'{bcolors.WARNING}Warning{bcolors.ENDC}')
    print(f'{bcolors.FAIL}Fail{bcolors.ENDC}')
    print('Normal')
