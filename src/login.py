from getpass import getpass

def get_favorites():
    favorites_id_list = []
    username_or_email = input('username (or email):')
    password = getpass('password:')

    print(username_or_email, password)

    return favorites_id_list

if __name__ == '__main__':
    get_favorites()
