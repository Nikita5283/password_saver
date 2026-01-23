import tkinter as tk
import subprocess
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry('280x90+400+170')


def change_color_but(event, but):
    but['bg'] = 'White'
    but['fg'] = 'Black'


def reset_color_but(event, but):
    but['bg'] = '#222123'
    but['fg'] = 'White'


def forget_wrong():
    wrong_lab.place_forget()
    wrong_but.place_forget()
    password_input['state'] = 'normal'
    root.geometry('280x90+400+170')


def forget_wrong_verif():
    wrong_lab.place_forget()
    wrong_but.place_forget()
    password_input['state'] = 'normal'
    root.geometry('280x120+400+170')


def normal_verif_inp(event):
    if not wrong_but.winfo_viewable():
        verification_input['state'] = 'normal'
        if verification_input.get() == 'Подтвердите пароль':
            verification_input.delete(0, tk.END)
    disabled_password_inp('check')


def normal_password_inp(event):
    if not wrong_but.winfo_viewable():
        password_input['state'] = 'normal'
        password_input_get = password_input.get()
        if password_input_get == 'Пароль' or password_input_get == 'Новый пароль':
            password_input.delete(0, tk.END)
        if verification_input.winfo_viewable() and verification_input['state'] != 'disabled':
            disabled_verif_inp()


def disabled_verif_inp():
    if not verification_input.get():
        verification_input.insert(0, 'Подтвердите пароль')
        verification_input['state'] = 'disabled'


def disabled_password_inp(event):
    if not password_input.get():
        password_input.insert(0, text_pass_input)
        password_input['state'] = 'disabled'
    if verification_input.winfo_viewable() and event != 'check':
        disabled_verif_inp()


main_background = tk.Frame(root, height=300, width=500, background='#363636')
main_background.place(relheight=1, relwidth=1)
main_background.bind('<Button-1>', disabled_password_inp)

guardian_img = ImageTk.PhotoImage(Image.open('images/pass.png').resize((65, 65)))
background_lab = tk.Label(root, image=guardian_img, background='#363636', width=170, height=40)
background_lab.place(x=55, y=2)
background_lab.bind('<Button-1>', disabled_password_inp)


def main():
    root.destroy()
    subprocess.call(['python', 'main.py'])


verification_get = []
previous_len_verif = 0


def memory_verif_pass(event, bind_type):
    global previous_len_verif
    global verification_get
    verif_get = verification_input.get()
    len_verif_get = len(verif_get)
    if previous_len_verif > len_verif_get:
        verification_get.pop(verification_input.index(tk.INSERT))
    if bind_type == 'KeyRel':
        for i in range(len_verif_get):
            if verif_get[i] != '●':
                verification_get.append(verif_get[i])
                verification_input.delete(i, i + 1)
                verification_input.insert(i, '●')
    previous_len_verif = len_verif_get


def check_verif_pass(event):
    global password_get
    global verification_get
    password = ''.join(verification_get)
    if ''.join(password_get) == password:
        with open('main_password.txt', 'w') as main_pass:
            main_pass.write(password)
        main()
    else:
        root.geometry('280x150+400+170')
        wrong_lab['text'] = 'Пароли не совпадают'
        wrong_lab.place(x=50, y=110)
        wrong_but.place(x=180, y=110)
        wrong_but['command'] = forget_wrong_verif
        password_input['state'] = 'disabled'
        verification_input['state'] = 'disabled'


main_password = ''
text_verification = tk.StringVar()
text_verification.set('Подтвердите пароль')
verification_input = tk.Entry(root, width=40, background='#222123', textvariable=text_verification, state='disabled',
                              disabledbackground='#222123', foreground='White', insertbackground='White',
                              disabledforeground='White', relief=tk.FLAT)
verification_input.bind('<Return>', check_verif_pass)
verification_input.bind('<KeyRelease>', lambda event: memory_verif_pass(event, 'KeyRel'))
verification_input.bind('<Key>', lambda event: memory_verif_pass(event, 'Key'))
verification_input.bind('<Button-1>', normal_verif_inp)

wrong_lab = tk.Label(root, background='#363636', foreground='White')
wrong_but = tk.Button(root, text='заново', command=forget_wrong, relief=tk.FLAT, width=6, background='#222123',
                      foreground='White', activebackground='White')
wrong_but.bind('<Enter>', lambda event: change_color_but(event, wrong_but))
wrong_but.bind('<Leave>', lambda event: reset_color_but(event, wrong_but))

password_get = []
previous_len_pass = 0


def memory_main_password(event, bind_type):
    global previous_len_pass
    global password_get
    pass_get = password_input.get()
    len_pass_get = len(pass_get)
    if previous_len_pass > len_pass_get:
        password_get.pop(password_input.index(tk.INSERT))
    if bind_type == 'KeyRel':
        for i in range(len_pass_get):
            if pass_get[i] != '●':
                password_get.append(pass_get[i])
                password_input.delete(i, i + 1)
                password_input.insert(i, '●')
    previous_len_pass = len_pass_get


def check_password(event):
    global main_password
    global password_get
    if main_password:
        if main_password == ''.join(password_get):
            main()
        else:
            root.geometry('280x120+400+170')
            wrong_lab['text'] = 'Неверный пароль'
            wrong_lab.place(x=60, y=80)
            wrong_but.place(x=180, y=80)
            password_input['state'] = 'disabled'
    else:
        root.geometry('280x120+400+170')
        verification_input.place(x=20, y=80)


text_password = tk.StringVar()
password_input = tk.Entry(root, width=40, background='#222123', textvariable=text_password,
                          state='disabled', disabledbackground='#222123', foreground='White',
                          disabledforeground='White',
                          insertbackground='White', relief=tk.FLAT)
password_input.place(x=20, y=50)
password_input.bind('<Button-1>', normal_password_inp)
password_input.bind('<KeyRelease>', lambda event: memory_main_password(event, 'KeyRel'))
password_input.bind('<Key>', lambda event: memory_main_password(event, 'Key'))
password_input.bind('<Return>', check_password)

text_pass_input = ''


def locked_screen():
    global text_pass_input
    global main_password
    with open('main_password.txt', 'r') as main_pass:
        main_password = main_pass.readline()
    if main_password:
        text_password.set('Пароль')
        text_pass_input = 'Пароль'
    else:
        text_password.set('Новый пароль')
        text_pass_input = 'Новый пароль'


locked_screen()
root.mainloop()
