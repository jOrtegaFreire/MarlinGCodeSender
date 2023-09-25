from windows import RootWindow


if __name__=="__main__":
    app=RootWindow("MarlinGcodeSender")
    app.resizable(False,False)
    app.mainloop()