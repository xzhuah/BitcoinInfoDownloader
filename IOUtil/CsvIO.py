# write content to a localfile filename
def writeToFile(filename, content):
    f = open(filename, 'w')
    f.write(content)
    f.close()


def appendToFile(filename, content):
    f = open(filename, 'a',encoding="utf-8")
    f.write(content + '\n')
    f.close()


def readFile(filename):
    file = open(filename, "r",encoding="utf-8")
    content = file.read()
    file.close()
    return content