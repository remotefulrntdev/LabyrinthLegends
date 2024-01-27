import json
import tkinter as tk
import tkinter.filedialog as fd
import webbrowser
import  os, subprocess, pathlib
import sys
root = tk.Tk()
root.title("New file - Notepad")
root.iconbitmap("img/icon.ico")
root.geometry("600x400")

font=("Consolas", 14)

# root.resizable(False, False)
menush = tk.Menu(root)

root.config(menu=menush)

# menush.add_command(label='File')
# menush.add_command(label='Edit')
# menush.add_command(label='Format')
# menush.add_command(label='Appearance')
# menush.add_command(label='Help')
def path_to_name(p):
    path = pathlib.PurePath(p)
    return path.name
def title_changer(pref, path):
    print(path)
    if path == "New file":
        root.title(f"New file - Notepad {pref}")
    else:
        root.title(f"{path_to_name(path)} - Notepad {pref}")

def cut():
    text_w.event_generate("<<Cut>>")

def copy():
    text_w.event_generate("<<Copy>>")

def paste():
    text_w.event_generate("<<Paste>>")

def create_f():
    global saved, current_path
    root.title("New file")
    text_w.delete(1.0,"end")
    saved = False
    current_path = ""
def new_window():
    subprocess.run(['python', "main.py"])
def open_f():
    global current_path
    file_p = fd.askopenfilename(title="Please select your file", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*")])
    if not current_path:
        current_path = "New file"
        return
    with open(file_p, "r",encoding='utf-8') as file:

        rl:list = file.readlines()
        rls = "\n".join(rl)
        text_w.delete("1.0", tk.END)

        text_w.insert(tk.END, rls)
        title_changer("", file_p)
        current_path =file_p

def typi(evt):
    title_changer("*", current_path)
def help():
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

def saving():
    global current_path
    # check is  file name basic
    if current_path == "New file":
        current_path = fd.asksaveasfilename(title="Please select your file to save", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*")])
        if not current_path:
            current_path = "New file"
            return

    title_changer("", current_path)
    # save to file
    txt_box_inf = text_w.get(1.0, tk.END)
    with open(current_path, mode="w") as f:
        f.write(txt_box_inf)
def saving_as():
    global current_path
    # check is  file name basic
    current_path = fd.asksaveasfilename(title="Please select your file to save as",defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*")])
    if not current_path:
        current_path = "New file"
        return

    title_changer("", current_path)
    # save to file
    txt_box_inf = text_w.get(1.0, tk.END)
    with open(current_path, mode="w") as f:
        f.write(txt_box_inf)

def fontik():
    global font
    font_p = fd.askopenfilename(title="Please select your font")
    if font_p != "":
        font = (font_p, font[1])
        text_w.config(font=font)
file_menu = tk.Menu(menush)
file_menu.add_command(label="Create               ",command=create_f)
file_menu.add_command(label="New window               ",command=new_window)
file_menu.add_command(label="Open               ", command=open_f)
file_menu.add_command(label="Save               ",command=saving)
file_menu.add_command(label="Save As               ",command=saving_as)
file_menu.add_separator()
file_menu.add_command(label="Print               ")
file_menu.add_separator()
file_menu.add_command(label="Exit               ",command=sys.exit)

menush.add_cascade(label="File", menu=file_menu)

edit_menu = tk.Menu(menush)
edit_menu.add_command(label="Cut               ",command=cut)
edit_menu.add_command(label="Copy               ", command=copy)
edit_menu.add_command(label="Paste               ", command=paste)

menush.add_cascade(label="Edit", menu=edit_menu)

format_menu = tk.Menu(menush)
format_menu.add_command(label="Font               ",command=fontik)
format_menu.add_command(label="Scale               ")
menush.add_cascade(label="Format", menu=format_menu)





help_menu = tk.Menu(menush)
help_menu.add_command(label="See help               ",command=help)



menush.add_cascade(label="Help", menu=help_menu)

text_w = tk.Text(root, wrap = "word", bg="white",font=font)
text_w.pack(expand="yes", fill="both")
text_w.bind("<KeyRelease>", typi)

saved = False
current_path = "New file"
with open("text.json",encoding="utf8") as f:
    fr = json.load(f)
text = fr["text"]
indx = -1
def typer():
    global indx
    indx += 1
    if indx < len(text):
        text_w.insert(tk.END, text[indx])
    else:
        print("end")
    root.after(50, typer)
root.after(50, typer)
# if __name__ == '__main__':
root.mainloop()


