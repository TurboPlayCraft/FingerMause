import tkinter as tk

class Notification(tk.Toplevel):
    open_notifications = []
    WIDTH = 200
    HEIGHT = 70
    
    def __init__(self, parent, title, message):
        super().__init__()
        self.title(title)
        self.geometry("{}x{}+20+20".format(Notification.WIDTH, Notification.HEIGHT)) # set the size and position
        self.configure(background='#333333') # set the background color
        self.attributes('-topmost', True) # make the notification always on top
        self.resizable(False, False) # disable resize
        self.overrideredirect(True) # remove the window border and title bar
        
        # create a frame to hold the label and button widgets
        frame = tk.Frame(self, bg='#333333')
        frame.pack(fill=tk.BOTH, expand=1)
        
        # create the message label with a transparent background
        message_label = tk.Label(frame, text=message, font=("Helvetica", 14), fg='#FFFFFF', bg='#333333', bd=0)
        message_label.configure(highlightthickness=0, highlightcolor="#333333", highlightbackground="#333333")
        message_label.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=1)
        message_label.configure(anchor="e")
        
        # set the opacity of the message label
        self.attributes("-alpha", 0.8)
        
        # set a timer to close the notification after 5 seconds
        self.after(4000, self.destroy)
        
        # add the notification to the list of open notifications
        Notification.open_notifications.insert(0,self)
        for i, notification in enumerate(Notification.open_notifications):
            x = self.winfo_screenwidth() - Notification.WIDTH - 20
            #y = 20 + (len(Notification.open_notifications) - 1) * (Notification.HEIGHT + 10)
            y = 20 + i * (Notification.HEIGHT + 10)
            notification.geometry("+{}+{}".format(x, y))

    def destroy(self):
        super().destroy()

        # remove the notification from the list of open notifications
        Notification.open_notifications.remove(self)
        
        # adjust the position of the remaining notifications
        for i, notification in enumerate(Notification.open_notifications):
            x = notification.winfo_screenwidth() - Notification.WIDTH - 20
            y = 20 + i * (Notification.HEIGHT + 10)
            notification.geometry("+{}+{}".format(x, y))

def show_notification(root, title, message):    
    # create the notification
    Notification(root,title, message)
    root.update()

# # create a hidden root window
# root = tk.Tk()
# root.withdraw()

# show_notification(root,"test1","1111111111")
# show_notification(root,"test2","2222222222")
# time.sleep(1)
# show_notification(root,"test3","3333333333")