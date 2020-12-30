import tkinter as tk
import threading
import time
from functools import partial
import praw
import smtplib, ssl
import env_variables

# reddit = praw.Reddit(
#     client_id="JYH3hMYpMdVCZg",
#     client_secret="B-k8FFQW-lSzWBc0IFQD9k6frinf_g",
#     user_agent="u/rlaxo",
#     username="rlaxo",
#     password="estrategia1"
# )


keywords = []
newposts = []
email = ""
password = ""
port = 465
context = ssl.create_default_context()
buttons = []


class MainApplication():

    def sendEmail(self, content):
        global email, password
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            server.sendmail(email, email, content)

    def startBtn(self, subreddit, keyword, mode):
        if (mode == "keyword"):
            self.is_running = True
            self.th = threading.Thread(target=partial(self.run, subreddit, keyword, mode))
            self.th.start()
        elif mode == "newposts":
            self.is_runningNew = True
            self.th = threading.Thread(target=partial(self.run, subreddit, keyword, mode))
            self.th.start()



    def run(self, sub, keyword, mode):
        global keywords, buttons
        global newposts

        if (mode == "keyword"):
            buttons[0]['state'] = "disabled"
            print("Started keyword search")
            for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new"):
                if (submission.title not in keywords):
                    keywords.append(submission.title)

            while (self.is_running == True):
                for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new", limit=5):
                    if (submission.title not in keywords):
                        self.sendEmail(submission.title)
                time.sleep(1)
        elif (mode == "newposts"):
            buttons[1]['state'] = "disabled"
            print("Started new posts search")
            for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new"):
                if (submission.title not in keywords):
                    newposts.append(submission.title)
            while (self.is_runningNew == True):
                for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new", limit=5):
                    self.sendEmail(submission.title)
                time.sleep(1)

    def stop(self, mode):
        try:
            if mode == "keyword":
                buttons[0]['state'] = "normal"
                print("Stopped keyword search")
                self.is_running = False
            elif mode == "newposts":
                buttons[1]['state'] = "normal"
                print("Stopped new posts search")
                self.is_runningNew = False
            self.th.join(0)
            self.th = None
        except (AttributeError, RuntimeError):  # beep thread could be None
            pass

    def getEmailandPwd(self):
        root = tk.Tk()
        emailbox = tk.Entry(root)
        pwdbox = tk.Entry(root, show='*')

        def onpwdentry(evt):
            global password
            global email
            email = emailbox.get()
            password = pwdbox.get()
            root.destroy()

        def onokclick():
            global password
            global email
            email = emailbox.get()
            password = pwdbox.get()
            root.destroy()

        def ondonotclick():
            root.destroy()
        tk.Label(root, text='Email').pack(side='top')
        emailbox.pack(side='top')
        tk.Label(root, text='Password').pack(side='top')
        pwdbox.pack(side='top')
        pwdbox.bind('<Return>', onpwdentry)
        tk.Button(root, command=onokclick, text='OK').pack(side='top')
        tk.Button(root, command=ondonotclick, text='Do not use email').pack(side='top')
        root.mainloop()

    def guiSetup(self):
        global buttons, email, password
        self.getEmailandPwd()
        window = tk.Tk()
        window.minsize(width=300, height=300)
        window.title("Reddit Notifier")

        lbl = tk.Label(window, text="Post Notifier")
        lbl.grid(row=0, column=0)

        field_label1 = tk.Label(window, text="Subreddit")
        field_label1.grid(row=1, column=0)
        field_entry1 = tk.Entry(window)
        field_entry1.grid(row=1, column=1)

        field_label2 = tk.Label(window, text="Keyword")
        field_label2.grid(row=2, column=0)
        field_entry2 = tk.Entry(window)
        field_entry2.grid(row=2, column=1)

        varBrowserCheck = tk.IntVar()
        browserCheck = tk.Checkbutton(window, text="Open in browser", variable=varBrowserCheck)
        browserCheck.grid(row=4, column=0)
        varEmailCheck = tk.IntVar()
        emailCheck = tk.Checkbutton(window, text="Send email", variable=varEmailCheck)
        emailCheck.grid(row=5, column=0)
        if email == "" and password == "":
            emailCheck['state'] = 'disabled'
        else:
            varEmailCheck.set(1)

        start = tk.Button(window, text='Alert new posts with keyword', width=25,
                          command=partial(self.startBtn, field_entry1, field_entry2, "keyword"))
        start.grid(row=1, column=2)

        stopKeywordSearch = tk.Button(window, text='Stop keyword search', width=25,
                                      command=partial(self.stop, "keyword"))
        stopKeywordSearch.grid(row=2, column=2)

        newPosts = tk.Button(window, text='Alert new posts', width=25,
                             command=partial(self.startBtn, field_entry1, field_entry2, "newposts"))
        newPosts.grid(row=4, column=2)

        stopNewPostSearch = tk.Button(window, text='Stop new posts search', width=25,
                                      command=partial(self.stop, "newposts"))
        stopNewPostSearch.grid(row=5, column=2)

        buttons.append(start)
        buttons.append(newPosts)
        buttons.append(emailCheck)
        buttons.append(browserCheck)
        window.mainloop()



if __name__ == "__main__":
    root = MainApplication()
    root.guiSetup()