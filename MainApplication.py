import tkinter as tk
import threading
import time
from functools import partial
import smtplib, ssl
from RedditAlert.env import env_variables
from selenium import webdriver

keywords = []
newposts = []
email = ""
password = ""
port = 465
context = ssl.create_default_context()
buttons = []


class MainApplication:
    """
    Method that opens a new chrome tab with passed url as parameter
    """
    def open_in_browser(self, url):
        driver = webdriver.Chrome()
        driver.get(url)

    """
    Method that sends email
    """
    def send_email(self, content):
        global email, password
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            server.sendmail(email, email, content)

    """
    Opens a new thread and sends the command to run
    """
    def start_btn(self, subreddit, keyword, mode):
        if mode == "keyword":
            self.is_running = True
            self.th = threading.Thread(target=partial(self.run, subreddit, keyword, mode))
            self.th.start()
        elif mode == "newposts":
            self.is_runningNew = True
            self.th = threading.Thread(target=partial(self.run, subreddit, keyword, mode))
            self.th.start()

    """
    Starts the tracking every 1 second
    """
    def run(self, sub, keyword, mode):
        global keywords, buttons
        global newposts

        if mode == "keyword":
            buttons[0]['state'] = "disabled"
            print("Started keyword search")
            for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new"):
                if submission.title not in keywords:
                    keywords.append(submission.title)

            while self.is_running:
                for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new", limit=5):
                    if submission.title not in keywords:
                        if buttons[3].get() == 1:
                            emailThread = threading.Thread(target=self.send_email, args=(submission.title,))
                            emailThread.start()
                        if buttons[4].get() == 1:
                            self.open_in_browser(submission.url)
                time.sleep(1)
        elif mode == "newposts":
            buttons[1]['state'] = "disabled"
            print("Started new posts search")
            for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new"):
                if submission.title not in keywords:
                    newposts.append(submission.title)
            while self.is_runningNew:
                for submission in env_variables.reddit.subreddit(sub.get()).search(keyword.get(), sort="new", limit=5):
                    if submission.title not in newposts:
                        if buttons[3].get() == 1:
                            emailThread = threading.Thread(target=self.send_email, args=(submission.title,))
                            emailThread.start()
                        if buttons[4].get() == 1:
                            self.open_in_browser(submission.url)
                time.sleep(1)
    """
    Stops the thread running currently
    @mode is mode to turn off
    """
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
    """
    Get gmail information to be able to send email and receive from itself.
    Turn on less secure app access on https://myaccount.google.com/lesssecureapps
    """
    def get_email_and_pwd(self):
        root = tk.Tk()
        emailbox = tk.Entry(root)
        pwdbox = tk.Entry(root, show='*')

        def on_pwd_entry(evt):
            global password
            global email
            email = emailbox.get()
            password = pwdbox.get()
            root.destroy()

        def on_ok_click():
            global password
            global email
            email = emailbox.get()
            password = pwdbox.get()
            root.destroy()

        def on_dont_click():
            root.destroy()

        tk.Label(root, text='Email').pack(side='top')
        emailbox.pack(side='top')
        tk.Label(root, text='Password').pack(side='top')
        pwdbox.pack(side='top')
        pwdbox.bind('<Return>', on_pwd_entry)
        tk.Button(root, command=on_ok_click, text='OK').pack(side='top')
        tk.Button(root, command=on_dont_click, text='Do not use email').pack(side='top')
        root.mainloop()

    """
    GUI setup
    Not using __init__ because of thread issues with tkinter
    """
    def guiSetup(self):
        global buttons, email, password
        self.get_email_and_pwd()
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

        var_browser_check = tk.IntVar()
        browser_check = tk.Checkbutton(window, text="Open in browser", variable=var_browser_check)
        browser_check.grid(row=4, column=0)
        var_email_check = tk.IntVar()
        email_check = tk.Checkbutton(window, text="Send email", variable=var_email_check)
        email_check.grid(row=5, column=0)
        if email == "" and password == "":
            email_check['state'] = 'disabled'
        else:
            var_email_check.set(1)

        start = tk.Button(window, text='Alert new posts with keyword', width=25,
                          command=partial(self.start_btn, field_entry1, field_entry2, "keyword"))
        start.grid(row=1, column=2)

        stop_keyword_search = tk.Button(window, text='Stop keyword search', width=25,
                                      command=partial(self.stop, "keyword"))
        stop_keyword_search.grid(row=2, column=2)

        new_posts = tk.Button(window, text='Alert new posts', width=25,
                             command=partial(self.start_btn, field_entry1, field_entry2, "newposts"))
        new_posts.grid(row=4, column=2)

        stop_new_posts_search = tk.Button(window, text='Stop new posts search', width=25,
                                      command=partial(self.stop, "newposts"))
        stop_new_posts_search.grid(row=5, column=2)

        # Add all buttons to a global array to have access to the buttons when needed
        buttons.append(start)
        buttons.append(new_posts)
        buttons.append(email_check)
        buttons.append(var_email_check)
        buttons.append(var_browser_check)
        buttons.append(browser_check)
        window.mainloop()


if __name__ == "__main__":
    root = MainApplication()
    root.guiSetup()
