import tkinter as tk
import librosa
import os
import filetype
from tkinter import filedialog, messagebox, simpledialog, ttk
from moviepy.editor import *
from moviepy.video.fx.resize import resize
from threading import *
from PIL import ImageTk, Image
import cv2
import numpy as np

LARGE_FONT= ("Verdana", 12)

def cast_to_clip(resource, resource_mime, duration_s):
    if 'image' in resource_mime:
        # If a GIF is chosen, must be loaded as VideoFileClip
        if 'gif' in resource_mime:
            visual_clip = VideoFileClip(resource)
            # Loop Gif for Duration of Audio File
            visual_clip = visual_clip.fx(vfx.loop, duration=duration_s)
            return visual_clip
        else:
            visual_clip = ImageClip(resource).set_duration(duration_s)
            return visual_clip
    elif 'video' in resource_mime:
        visual_clip = VideoFileClip(resource, audio=False)
        # Loop Video file if it has shorter duration than the audio file
        if duration_s > visual_clip.duration:
            visual_clip = visual_clip.fx(vfx.loop, duration=duration_s)
        return visual_clip

class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        # Parent refers to Root window
        self.parent = parent
        self.frames = {}

        self.menubar = tk.Menu(parent)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Create New Video", command = lambda: MainPage.create_video(parent))
        filemenu.add_command(label="Exit", command=quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(parent, menu=filemenu)

        # Create Main Menu Frame from MainPage Class
        frame = MainPage(parent, self)
        frame.pack(side="top", fill="both", expand = True)

        self.frames[MainPage] = frame

        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Display Background Image
        self.bg_image = Image.open('Assets/BG_IM.jpg')
        self.bg_im = ImageTk.PhotoImage(self.bg_image)
        bg_im_label = tk.Label(self, image=self.bg_im)
        bg_im_label.place(x=0, y=0, relwidth=1, relheight=1)

        create_video_button = tk.Button(self, fg='#FFFFFF', background='#000000', activebackground='#44DDFF', font=('Verdana', 12, 'bold italic'), activeforeground='white', text='Create New Video', padx=2, pady=2, command = self.create_video)
        create_video_button.pack(pady=10,padx=10, side=tk.TOP, fill='y')

        create_animated_video_button = tk.Button(self, fg='#FFFFFF', background='#000000', activebackground='#44DDFF', font=('Verdana', 12, 'bold italic'), activeforeground='white', text='Create New Animated Video', padx=2, pady=2, command = self.create_animated_video)
        create_animated_video_button.pack(pady=10,padx=10, side=tk.TOP, fill='y')

        play_video_button = tk.Button(self, fg='#FFFFFF', background='#000000', activebackground='#44DDFF', font=('Verdana', 12, 'bold italic'), activeforeground='white', text='Play A Video', padx=2, pady=2, command = self.play_video)
        play_video_button.pack(pady=10,padx=10, side=tk.TOP, fill='y', anchor='center')

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
        # Flag for Custom Dimensions
        custom_dims = False
        response = messagebox.askquestion('Use Custom Dimensions?', 'Do you want to specify custom Dimensions? Defaults to 1920x1080')
        if response == 'yes':
            ui_width = simpledialog.askinteger(title='Specify Width', prompt='Specify the Video Width')
            ui_height = simpledialog.askinteger(title='Specify Height', prompt='Specify the Video Height')
            if ui_width and ui_height:
                custom_dims = True
            else:
                print('Missing Dimension Input. Defaulting to 1920x1080')

        if selected_audio and selected_visual:
            audio_path = os.path.basename(str(selected_audio))
            audio= AudioFileClip(selected_audio, fps=44100)
            visual_clip = None

            visual_clip = cast_to_clip(selected_visual, selected_visual_mime, duration_s)

            if custom_dims:
                visual_clip = resize(visual_clip, (ui_width, ui_height))

            response = messagebox.askquestion('Add Watermark', 'Do you want to add a Watermark?')
            watermark_clip = None
            if response == 'yes':
                watermark = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select The Image For The Watermark')
                watermark_type = filetype.guess(watermark)
                watermark_mime = watermark_type.mime
                if watermark:
                    print(f'Adding Watermark: {watermark}')
                    factor_table = {'50%': 2, '33%': 3, '25%': 4, '20%': 5}
                    factor = 5
                    factor =  simpledialog.askstring('Specify Scale of Watermark', 'Specify Scale of Watermark from [50%, 33%, 25%, 20%]')
                    if isinstance(factor, str) and factor in factor_table.keys():
                        factor = factor_table[factor]
                        print(f'Watermark Scale set to [{factor}]')

                    if 'image' in watermark_mime:
                        watermark_clip = (ImageClip(watermark).
                                         set_duration(duration_s).
                                         resize((width/factor, height/factor)).
                                         set_pos(('right','bottom')) )
                    elif 'gif' in watermark_mime or 'video' in watermark_mime:
                        watermark_clip = (VideoFileClip(watermark).
                                         resize((width/factor, height/factor)).
                                         set_pos(('right','bottom')) )
                        watermark_clip = watermark_clip.fx(vfx.loop, duration=duration_s)

            if visual_clip:
                clip = visual_clip.set_audio(audio).set_duration(duration_s)
                if watermark_clip:
                    clip = CompositeVideoClip([clip,watermark_clip])
                clip.write_videofile('Exports/Test.mp4', fps=30)

    def create_animated_video(self):
        # Load in Audio file
        selected_audio  = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select Audio File')
        if not selected_audio:
            return
        else:
            print(f'Selected Audio File: {selected_audio}')
            duration_s = librosa.get_duration(filename=selected_audio)
            duration_m = duration_s/60
            print(f'Duration in Seconds: {duration_s}')
            print(f'Duration in Seconds: {duration_m}')

        # Load in Image/Video to use as Background
        selected_background = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select The Background For The Video')
        selected_background_type = filetype.guess(selected_background)
        selected_background_mime = selected_background_type.mime
        print(selected_background_mime)
        if not selected_background:
            return
        else:
            print(f'Selected Background File: {selected_background}')

        # Load in Image to be Animated
        selected_animation = filedialog.askopenfilename(parent=self, initialdir='Resources/', title='Select The Asset to Animate. Transparent PNGs work best')
        selected_animation_type = filetype.guess(selected_animation)
        selected_animation_mime = selected_animation_type.mime
        print(selected_background_mime)
        if not selected_animation:
            return
        else:
            print(f'Selected File for Animation: {selected_animation}')
            image = Image.open(selected_animation)
            animation_width, animation_height = image.size

        width = 1920
        height = 1080
        vid_size = width, height
        # Flag for Custom Dimensions
        custom_dims = False
        response = messagebox.askquestion('Use Custom Dimensions?', 'Do you want to specify custom Dimensions? Defaults to 1920x1080')
        if response == 'yes':
            ui_width = simpledialog.askinteger(title='Specify Width', prompt='Specify the Video Width')
            ui_height = simpledialog.askinteger(title='Specify Height', prompt='Specify the Video Height')
            if ui_width and ui_height:
                custom_dims = True
            else:
                print('Missing Dimension Input. Defaulting to 1920x1080')

        if selected_audio and selected_background and selected_animation:
            audio_path = os.path.basename(str(selected_audio))
            audio= AudioFileClip(selected_audio, fps=44100)
            bg_visual_clip = None
            animation_clip = None

            # Determine Type and Cast to Moviepy Clip
            bg_visual_clip = cast_to_clip(selected_background, selected_background_mime, duration_s)
            if custom_dims:
                bg_visual_clip = resize(bg_visual_clip, (ui_width, ui_height))

            if selected_animation:
                factor_table = {'50%': 2, '33%': 3, '25%': 4, '20%': 5}
                factor = 5
                factor =  simpledialog.askstring('Specify Scale of Animated Visual', 'Specify Scale of Animated Visual from [50%, 33%, 25%, 20%]')
                if isinstance(factor, str) and factor in factor_table.keys():
                    factor = factor_table[factor]
                    print(f'Watermark Scale set to [{factor}]')

                if 'image' in selected_animation_mime:
                    animation_clip = (ImageClip(selected_animation).
                                     set_duration(duration_s).
                                     resize((animation_width/factor, animation_height/factor)).
                                     set_pos(('center','center')) )
                elif 'gif' in selected_animation_mime or 'video' in selected_animation_mime:
                    animation_clip = (VideoFileClip(selected_animation).
                                     resize((animation_width/factor, animation_height/factor)).
                                     set_pos(('center','center')) )
                    animation_clip = animation_clip.fx(vfx.loop, duration=duration_s)

                animation_clip = animation_clip.fx(vfx.rotate, lambda duration_s: 90*duration_s, expand=False).set_duration(duration_s)

                if bg_visual_clip and animation_clip:
                    bg_clip = bg_visual_clip.set_audio(audio).set_duration(duration_s)
                    clip = CompositeVideoClip([bg_clip, animation_clip])
                    clip.write_videofile('Exports/Test.mp4', fps=30)

    def play_video(self):
            video_fpath = filedialog.askopenfilename(parent=self, initialdir='Exports/', title='Select A Video')
            if video_fpath:
                print(f'Playing Video: {video_fpath}')
                video_window = VideoWindow(self, video_fpath)
            else:
                file_list =  glob.glob('Exports/*')
                try:
                    latest_file = max(file_list, key=os.path.getctime)
                except Exception as ex:
                    messagebox.showinfo('Error!', 'Could Not Find A Video To Play')
                    return

class VideoWindow(tk.Frame):
    def __init__(self, parent, video_fpath):
        tk.Frame.__init__(self, parent)
        self.video_fpath = video_fpath
        self.play_video()
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()

    def play_video(self):
        self.cap = cv2.VideoCapture(self.video_fpath)
        still_playing = True

        while(still_playing):
            # Capture frame-by-frame
            ret, frame = self.cap.read()

            # Display the resulting frame
            try:
                cv2.imshow('Video', frame)
            except Exception as ex:
                print('Video Ended')
                self.cap.release()
                cv2.destroyAllWindows()
                return

            if cv2.waitKey(25) & 0xFF == ord('q'):
                still_playing = False

if __name__ == '__main__':
    root = tk.Tk()
    root.title('PromoGen 9000')
    root.resizable(False, False)
    root.geometry('300x300')
    MainApplication(root).pack(side='top', fill='both', expand=False)
    root.mainloop()
