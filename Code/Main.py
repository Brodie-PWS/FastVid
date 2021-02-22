import tkinter as tk
import librosa
import os
import filetype
from tkinter import filedialog, messagebox, simpledialog, ttk
from moviepy.editor import *
from threading import *

LARGE_FONT= ("Verdana", 12)

class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frames = {}

        self.menubar = tk.Menu(parent)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Create New Video", command = lambda: MainPage.create_video)
        filemenu.add_command(label="Exit", command=quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(parent, menu=filemenu)

        # Create Main Menu Frame from MainPage Class
        frame = MainPage(parent, self)
        frame.pack(side="top", fill="both", expand = True)
        self.frames[MainPage] = frame

        # frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        create_video_button = tk.Button(self, fg='#333276', background='#44DDFF', activebackground='#44DDFF', font=('Verdana', 12, 'bold italic'), activeforeground='white', text='Create New Video', padx=2, pady=2, command = self.create_video)
        create_video_button.pack(pady=15,padx=10, side=tk.BOTTOM)

    def create_video(self):
        selected_audio  = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select Audio File')
        if not selected_audio:
            return
        else:
            print(f'Selected Audio File: {selected_audio}')
            duration_s = librosa.get_duration(filename=selected_audio)
            duration_m = duration_s/60
            print(f'Duration in Seconds: {duration_s}')
            print(f'Duration in Seconds: {duration_m}')

        selected_visual = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select The Image For The Video')
        selected_visual_type = filetype.guess(selected_visual)
        selected_visual_mime = selected_visual_type.mime
        print(selected_visual_mime)
        if not selected_visual:
            return
        else:
            print(f'Selected Image File: {selected_visual}')

        width = 1920
        height = 1080
        vid_size = width, height
        response = messagebox.askquestion('Use Custom Dimensions?', 'Do you want to specify custom Dimensions? Defaults to 1920x1080')
        if response == 'yes':
            ui_width = simpledialog.askinteger(title='Specify Width', prompt='Specify the Video Width')
            ui_height = simpledialog.askinteger(title='Specify Height', prompt='Specify the Video Height')
            if ui_width and ui_height:
                vid_size = ui_width, ui_height
            else:
                print('Missing Dimension Input. Defaulting to 1920x1080')

        if selected_audio and selected_visual:
            audio_path = os.path.basename(str(selected_audio))
            audio= AudioFileClip(selected_audio, fps=44100)

            # Check file type to determine flow
            if 'image' in selected_visual_mime:
                # If a GIF is chosen, must be loaded as VideoFileClip
                if 'gif' in selected_visual_mime:
                    visual_clip = VideoFileClip(selected_visual)
                    # Loop Gif for Duration of Audio File
                    visual_clip = visual_clip.fx(vfx.loop, duration=duration_s)

                    clip = visual_clip.set_audio(audio).set_duration(duration_s)
                    clip.write_videofile('Exports/Test.mp4', fps=30)
                else:
                    visual_clip = ImageClip(selected_visual).set_duration(duration_s)

                    clip = visual_clip.set_audio(audio)
                    clip.write_videofile('Exports/Test.mp4', fps=30)

            elif 'video' in selected_visual_mime:
                visual_clip = VideoFileClip(selected_visual, audio=False)

                # Loop Video file if it has shorter duration than the audio file
                if duration_s > visual_clip.duration:
                    looped_clip = visual_clip.fx(vfx.loop, duration=duration_s)

                    clip = looped_clip.set_audio(audio)
                    clip.write_videofile('Exports/Test.mp4', fps=30)
                else:
                    clip = visual_clip.set_audio(audio).set_duration(duration_s)
                    clip.write_videofile('Exports/Test.mp4', fps=30)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('PromoGen 9000')
    root.resizable(False, False)
    root.geometry('300x300')
    MainApplication(root).pack(side='top', fill='both', expand=True)
    root.mainloop()