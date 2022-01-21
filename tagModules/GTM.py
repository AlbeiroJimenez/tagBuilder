import samples_util as g_util

class containerGTM:
    def __init__(self):
        pass

scope = ['https://www.googleapis.com/auth/tagmanager.edit.containers']

if __name__ == '__main__':
    g_util.get_credentials()
    print("Todo Ok")