import logging





def newUser(combo, username):
    f = open('login.txt', 'r', encoding='utf-8')
    line = f.readline()
    while line:
        existingUsername = line.split(';')
        if existingUsername[0] == username:
            return False
        line = f.readline()
    f.close()
    f = open('login.txt', 'a', encoding='utf-8')
    f.write(combo + '\n')
    f.close()
    return True

def authenticate(combo):
    with open('login.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            if line.rstrip() == combo.rstrip():
                return True
            line = f.readline()
    return False

def log(user, activity, fileName):
    logging.basicConfig(filename=fileName, level=logging.INFO, format='%(message)s:%(asctime)s')
    logging.info(f'User: {user}, Activity: {activity}, Date/Time ')


log('Smith, John', 'log in', 'test.log')