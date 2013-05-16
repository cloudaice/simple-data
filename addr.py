#-*-coding: utf-8-*-

def searchpage(p):
    if p == 1:
        return "https://github.com/search?q=location:china&s=followers&type=Users"
    else:
        return "https://github.com/search?p=" + str(p) + "&q=location:china&s=followers&type=Users"
