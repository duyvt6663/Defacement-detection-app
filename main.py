import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import *
from test import *
from threading import Thread

class CircularProgressbar(object):
    def __init__(self, canvas, x0, y0, x1, y1, width=2, start_ang=0, full_extent=360.):
        self.custom_font = tkFont.Font(family="Helvetica", size=12, weight='bold')
        self.canvas = canvas
        self.x0, self.y0, self.x1, self.y1 = x0+width, y0+width, x1-width, y1-width
        self.tx, self.ty = (x1-x0) / 2, (y1-y0) / 2
        self.width = width
        self.start_ang, self.full_extent = start_ang, full_extent
        # draw static bar outline
        w2 = width / 2
        self.oval_id1 = self.canvas.create_oval(self.x0-w2, self.y0-w2,
                                                self.x1+w2, self.y1+w2)
        self.oval_id2 = self.canvas.create_oval(self.x0+w2, self.y0+w2,
                                                self.x1-w2, self.y1-w2)

    def start(self, interval=50):
        self.interval = interval  # Msec delay between updates.
        self.increment = self.full_extent / interval
        self.extent = 0
        self.arc_id = self.canvas.create_arc(self.x0, self.y0, self.x1, self.y1,
                                             start=self.start_ang, extent=self.extent,
                                             width=self.width, style='arc')
        percent = '0%'
        self.label_id = self.canvas.create_text(self.tx, self.ty, text=percent,
                                                font=self.custom_font)

    def step(self, delta):
        """Increment extent and update arc and label displaying how much completed."""
        self.extent = self.extent + delta

        if self.extent > self.cap:
            filled_extent = self.cap if self.cap < self.full_extent else self.full_extent-0.001
            self.canvas.itemconfigure(self.arc_id, extent=filled_extent)
            # Update percentage value displayed.
            percent = '{:.2f}%'.format(self.cap / self.full_extent * 100)
            self.canvas.itemconfigure(self.label_id, text=percent)
            # reset
            self.extent = 0
            return
        
        self.canvas.itemconfigure(self.arc_id, extent=self.extent)
        # Update percentage value displayed.
        percent = '{:.2f}%'.format(self.extent / self.full_extent * 100)
        self.canvas.itemconfigure(self.label_id, text=percent)

        # recurse to animate
        self.canvas.after(self.interval, self.step, delta)

    def set_progress(self, percent):
        self.extent = 0
        self.cap = min(percent*360, 360)
        # print(self.cap)
        self.canvas.itemconfigure(self.arc_id, extent=self.extent)

        # Update percentage value displayed.
        self.canvas.itemconfigure(self.label_id, text='{:.0f}%'.format(percent*100))
        self.canvas.after(self.interval, self.step, self.increment)   

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def check(self, url):
        try:
            # clear text from url box
            self.url.delete(0, "end")

            model = load_model("./models/our_model.h5")
            res = []
            t = Thread(target=check, args=(url, model, res))
            t.start(), t.join()
            alert, score = res[0], res[1]

            self.label.config(text = alert)
            self.progressbar.set_progress(score) 
        except:
            self.label.config(text = "Something wrong with the URL")

    def createWidgets(self):
        row = 0 # widgets' state

        self.label = Label(self, text='', font=("Helvetica", 19))

        Label(self, text='URL:', font=("Helvetica", 13)).grid(column=0, padx=10, row=row)
        self.url = tk.Entry(self, width=40, borderwidth=2)
        self.url.bind("<Return>", lambda e: self.check(self.url.get()))
        self.url.grid(column=1, row=row)
        row += 1

        self.label.grid(row=row, column=0, columnspan=2)
        row += 1

        self.canvas = tk.Canvas(self, width=200, height=200, bg='white')
        self.canvas.grid(row=row, column=0, columnspan=2)
        self.progressbar = CircularProgressbar(self.canvas, 0, 0, 200, 200, 20)
        row += 1

    def start(self):
        self.progressbar.start()
        self.mainloop()

if __name__ == '__main__':
    app = Application()
    app.master.title('Monitoring app')
    app.start()