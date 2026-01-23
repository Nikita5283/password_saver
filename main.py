import os.path
import tkinter as tk
from PIL import Image, ImageTk
import pickle

main_root = tk.Tk()
main_root.geometry('500x300+400+170')


def change_color_but(event):
    event.widget['bg'] = '#D1D1D1'
    event.widget['fg'] = 'Black'


def reset_color_but(event):
    event.widget['bg'] = '#222123'
    event.widget['fg'] = '#D1D1D1'


# #363636
main_background = tk.Frame(main_root, height=300, width=500, background='#222123')
main_background.place(relheight=1, relwidth=1)

add_black_img = ImageTk.PhotoImage(Image.open('images/add_black.png').resize((35, 35)))
add_white_img = ImageTk.PhotoImage(Image.open('images/add_white.png').resize((35, 35)))
lock_img = ImageTk.PhotoImage(Image.open('images/lock.png').resize((110, 110)))
arrow_img = ImageTk.PhotoImage(Image.open('images/arrow.png').resize((10, 10)))
enter_black_img = ImageTk.PhotoImage(Image.open('images/enter_black.png').resize((15, 15)))
enter_white_img = ImageTk.PhotoImage(Image.open('images/enter_white.png').resize((15, 15)))
card_black_img = ImageTk.PhotoImage(Image.open('images/card_black.png').resize((15, 15)))
card_white_img = ImageTk.PhotoImage(Image.open('images/card_white.png').resize((15, 15)))
folder_black_img = ImageTk.PhotoImage(Image.open('images/folder_black.png').resize((15, 15)))
folder_white_img = ImageTk.PhotoImage(Image.open('images/folder_white.png').resize((15, 15)))
write_black_img = ImageTk.PhotoImage(Image.open('images/write_black.png').resize((15, 15)))
write_white_img = ImageTk.PhotoImage(Image.open('images/write_white.png').resize((15, 15)))

lock_img_lab = tk.Label(main_root, image=lock_img, background='#222123')
lock_img_lab.place(x=190, y=90)

dist = 5
folders_files = {}


def add_write(e, name_folder, fold_root):
    add_root = tk.Toplevel(main_root)
    add_root.geometry('195x175+560+210')

    type_write = 'enter'

    def ok(e=None):
        global folders_files

        dist_wr = 0
        write_title = title.get()

        def warn(text):
            warning = tk.Toplevel(add_root)
            warning.geometry('250x60+530+250')
            warn_background = tk.Frame(warning, height=300, width=500, background='#D1D1D1')
            warn_background.place(relheight=1, relwidth=1)
            warn_lab = tk.Label(warning, text=text, background='#D1D1D1')
            warn_lab.place(x=5, y=0)

        if os.path.exists(f'{name_folder}/{write_title}.txt'):
            warn('Запись с таким названием уже существует')
        else:
            write_but = tk.Button(fold_root, text=write_title, width=460, background='#222123',
                                  foreground='#D1D1D1',
                                  relief=tk.FLAT, activebackground='White', image=write_white_img,
                                  compound=tk.LEFT,
                                  padx=10, anchor='w', height=15)
            write_but.bind('<Button-1>', lambda event: write(event))
            write_but.bind('<Enter>', lambda event, picture=write_black_img: add_anim(event, picture, 'change'))
            write_but.bind('<Leave>', lambda event, picture=write_white_img: add_anim(event, picture, 'reset'))
            write_but.place(x=5, y=dist_wr)
            dist_wr += 24
            if type_write == 'enter':
                login_get = login.get()
                password_get = password.get()
                add_root.destroy()
                with open(f'{name_folder}/{write_title}.txt', 'w') as f:
                    f.write(f'{login_get}\n{password_get}')
                folders_files[write_title] = {write_title: [login_get, password_get]}
            elif type_write == 'pay_card':
                card_number_get = card_number.get()
                pin_get = pin.get()
                cvv_get = cvv.get()
                term_get = term.get()
                add_root.destroy()
                with open(f'{name_folder}/{write_title}.txt', 'w') as f:
                    f.write(f'{card_number_get}\n{pin_get}\n{cvv_get}\n{term_get}')
                folders_files[write_title] = {write_title: [card_number_get, pin_get, cvv_get, term_get]}
        with open('hierarchy.bin', 'wb') as directory:
            pickle.dump(folders_files, directory)

    def types_write_unlock(e=None):
        if enter.winfo_viewable():
            enter.place_forget()
            pay_card.place_forget()
        else:
            enter.place(x=5, y=57)
            pay_card.place(x=5, y=78)

    def normal(e, widget, widget_text):
        widget['state'] = 'normal'

        if widget.get() == widget_text:
            widget.delete(0, tk.END)
            for wid, text in write_widgets.items():
                if not wid.get() and widget is not wid:
                    wid.insert(0, text)
                    wid['state'] = 'disabled'
        if type_write == 'enter':
            ok_but['state'] = 'normal' if title.get() and login.get() and password.get() and \
                                          title['state'].startswith('n') and login['state'].startswith('n') and \
                                          password['state'].startswith('n') else 'disabled'
        elif type_write == 'pay_card':
            pass

    def disabled_all(e):
        for widget, text in write_widgets.items():
            if not widget.get():
                widget.insert(0, text)
                widget['state'] = 'disabled'
        enter.place_forget()
        pay_card.place_forget()

    def add_wr():
        types_write_lab['text'] = 'Вход'
        ok_but.place(x=130, y=145)
        close_but.place(x=65, y=145)
        title.place(x=5, y=65)
        login.place(x=5, y=90)
        password.place(x=5, y=115)
        types_write_lab.place(x=5, y=35)
        types_write_but.place(x=70, y=35)

    def enter_type():
        nonlocal type_write
        add_root.geometry('195x175+560+210')
        types_write_lab['text'] = 'Вход'
        enter.place_forget()
        pay_card.place_forget()
        card_number.place_forget()
        pin.place_forget()
        cvv.place_forget()
        term.place_forget()
        login.place(x=5, y=90)
        password.place(x=5, y=115)
        ok_but.place(x=130, y=145)
        close_but.place(x=65, y=145)
        type_write = 'enter'

    def pay_card_type():
        nonlocal type_write
        add_root.geometry('195x200+560+210')
        types_write_lab['text'] = 'Карта'
        enter.place_forget()
        pay_card.place_forget()
        login.place_forget()
        password.place_forget()
        card_number.place(x=5, y=90)
        cvv.place(x=100, y=115)
        term.place(x=5, y=115)
        pin.place(x=5, y=140)
        ok_but.place(x=130, y=170)
        close_but.place(x=65, y=170)
        type_write = 'pay_card'

    background = tk.Frame(add_root, height=250, width=480, background='#363636')
    background.place(relheight=1, relwidth=1)
    background.bind('<Button-1>', disabled_all)

    write_but = tk.Button(add_root, background='#363636', foreground='White', text='Запись', width=7, relief=tk.FLAT,
                          command=add_wr, activebackground='#363636', activeforeground='White')
    write_but.place(x=59, y=0)

    ok_but = tk.Button(add_root, background='#222123', foreground='White', text='ок', width=7, relief=tk.FLAT,
                       command=ok,
                       state='disabled', activeforeground='White', activebackground='Black')

    close_but = tk.Button(add_root, background='#222123', foreground='White', text='отмена', width=7, relief=tk.FLAT,
                          activeforeground='White', activebackground='Black')

    title = tk.Entry(add_root, background='#222123', foreground='White',
                     disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                     insertbackground='White', width=30, relief=tk.FLAT)

    login = tk.Entry(add_root, background='#222123', foreground='White',
                     disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                     insertbackground='White', width=30, relief=tk.FLAT)

    password = tk.Entry(add_root, background='#222123', foreground='White',
                        disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                        insertbackground='White', width=30, relief=tk.FLAT)

    card_number = tk.Entry(add_root, background='#222123', foreground='White',
                           disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                           insertbackground='White', width=30, relief=tk.FLAT)

    pin = tk.Entry(add_root, background='#222123', foreground='White',
                   disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                   insertbackground='White', width=30, relief=tk.FLAT)

    cvv = tk.Entry(add_root, background='#222123', foreground='White',
                   disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                   insertbackground='White', width=14, relief=tk.FLAT)

    term = tk.Entry(add_root, background='#222123', foreground='White', disabledforeground='LightGrey',
                    disabledbackground='#222123', state='disabled', insertbackground='White', width=14, relief=tk.FLAT)

    types_write_lab = tk.Label(add_root, text='Вход', width=10, background='#222123', foreground='White')
    types_write_lab.bind('<Button-1>', types_write_unlock)

    types_write_but = tk.Button(add_root, image=arrow_img, background='#222123', relief=tk.FLAT,
                                activebackground='Black',
                                width=15, height=15, command=types_write_unlock)

    enter = tk.Button(add_root, image=enter_white_img, compound=tk.LEFT, width=60, background='#222123', relief=tk.FLAT,
                      activebackground='White', text='Вход', foreground='White', activeforeground='Black', padx=10,
                      anchor='w', height=13, command=enter_type)

    enter.bind('<Enter>', lambda event, picture=enter_black_img: add_anim(event, picture, 'change'))
    enter.bind('<Leave>', lambda event, picture=enter_white_img: add_anim(event, picture, 'reset'))

    pay_card = tk.Button(add_root, image=card_white_img, compound=tk.LEFT, width=60, background='#222123',
                         relief=tk.FLAT,
                         activebackground='White', text='Карта', foreground='White', activeforeground='Black',
                         padx=10, anchor='w', height=13, command=pay_card_type)

    pay_card.bind('<Enter>', lambda event, picture=card_black_img: add_anim(event, picture, 'change'))
    pay_card.bind('<Leave>', lambda event, picture=card_white_img: add_anim(event, picture, 'reset'))

    write_widgets = {title: 'Название', login: 'Логин', password: 'Пароль',
                     card_number: 'Номер карты', pin: 'ПИН-код', cvv: 'CVV-код', term: 'срок(мм/гг)'}

    for w in write_widgets:
        w.bind('<Button-1>', lambda event, widget=w, text=write_widgets[w]: normal(event, widget, text))
        w.bind('<KeyRelease>', lambda event, widget=w, text=write_widgets[w]: normal(event, widget, text))
        text_wid = tk.StringVar()
        text_wid.set(write_widgets[w])
        w['textvariable'] = text_wid
    add_wr()


def fold(e):
    name_folder = e.widget['text']

    folder_root = tk.Toplevel(main_root)

    dist = 0
    for name_write in folders_files[name_folder]:
        write_in_folder = tk.Button(folder_root, text=name_write, width=69, background='Black', foreground='White',
                                    relief=tk.FLAT)
        write_in_folder.bind('<Button-1>', write)
        write_in_folder.place(x=5, y=dist)
        dist += 30
    folder_root.geometry('400x200+450+225')
    folder_root.title(name_folder)

    background = tk.Frame(folder_root, height=300, width=500, background='#222123')
    background.place(relheight=1, relwidth=1)

    add_pass = tk.Button(folder_root, compound=tk.LEFT, padx=10, anchor='w', width=35,
                         relief=tk.FLAT, background='#222123', activebackground='#222123', activeforeground='Black',
                         foreground='White', image=add_white_img)
    add_pass.place(x=350, y=152)
    add_pass.bind('<Button-1>',
                  lambda event, name_fold=name_folder, root=folder_root: add_write(event, name_fold, root))
    add_pass.bind('<Enter>', lambda event, picture=add_black_img: add_anim(event, picture))
    add_pass.bind('<Leave>', lambda event, picture=add_white_img: add_anim(event, picture))


def write(e):
    name_write = e.widget['text']

    file_root = tk.Toplevel(main_root)
    file_root.geometry('400x200+450+225')
    file_root.title(name_write)

    background = tk.Frame(file_root, height=300, width=500, background='#222123')
    background.place(relheight=1, relwidth=1)

    data_lab = tk.Label(file_root, background='#222123', foreground='White',
                        text=f'Логин: {folders_files[name_write][name_write][0]}\nПароль: {folders_files[name_write][name_write][1]}')
    data_lab.place(x=5, y=5)


def main(start=(True,)):
    global dist, folders_files
    try:
        with open('hierarchy.bin', 'rb') as directory:
            direct = pickle.load(directory)
        folders_files = direct
        lock_img_lab.place_forget()
        for name_write in direct:
            if type(direct[name_write]) is dict:
                write_but = tk.Button(main_root, text=name_write, width=460, background='#222123',
                                      foreground='#D1D1D1',
                                      relief=tk.FLAT, activebackground='White', image=write_white_img,
                                      compound=tk.LEFT,
                                      padx=10, anchor='w', height=15)
                write_but.bind('<Button-1>', lambda event: write(event))
                write_but.bind('<Enter>', lambda event, picture=write_black_img: add_anim(event, picture, 'change'))
                write_but.bind('<Leave>', lambda event, picture=write_white_img: add_anim(event, picture, 'reset'))
                write_but.place(x=5, y=dist)
                dist += 24
            else:
                folder = tk.Button(main_root, text=name_write, width=460, background='#222123', foreground='#D1D1D1',
                                   relief=tk.FLAT, activebackground='White', image=folder_white_img, compound=tk.LEFT,
                                   padx=10, anchor='w', height=15)
                folder.bind('<Button-1>', lambda event: fold(event))
                folder.bind('<Enter>', lambda event, picture=folder_black_img: add_anim(event, picture, 'change'))
                folder.bind('<Leave>', lambda event, picture=folder_white_img: add_anim(event, picture, 'reset'))
                folder.place(x=5, y=dist)
                dist += 24
    except EOFError:
        pass


def add_anim(e, pic, change_color=''):
    e.widget['image'] = pic
    if change_color:
        change_color_but(e) if change_color == 'change' else reset_color_but(e)


def add():
    add_root = tk.Toplevel(main_root)

    type_add = 'folder'
    type_write = 'enter'

    def normal(e, widget, widget_text):
        widget['state'] = 'normal'

        if widget.get() == widget_text:
            widget.delete(0, tk.END)
            for wid, text in write_widgets.items():
                if not wid.get() and widget is not wid:
                    wid.insert(0, text)
                    wid['state'] = 'disabled'
        if widget is name_fold:
            ok_but['state'] = 'normal' if name_fold.get() else 'disabled'
        else:
            if type_write == 'enter':
                ok_but['state'] = 'normal' if title.get() and login.get() and password.get() and \
                                              title['state'].startswith('n') and login['state'].startswith('n') and \
                                              password['state'].startswith('n') else 'disabled'
            elif type_write == 'pay_card':
                pass

    def warn(text):
        warning = tk.Toplevel(add_root)
        warning.geometry('250x60+530+250')
        warn_background = tk.Frame(warning, height=300, width=500, background='#D1D1D1')
        warn_background.place(relheight=1, relwidth=1)
        warn_lab = tk.Label(warning, text=text, background='#D1D1D1')
        warn_lab.place(x=5, y=0)

        ok_warn_but = tk.Button(warning, background='#222123', foreground='White', text='понятно', width=7,
                                relief=tk.FLAT, command=lambda warn=warning: warn.destroy())
        ok_warn_but.place(x=5, y=25)

    def ok(e=None):
        global dist
        global folders_files
        name_fol = name_fold.get()
        lock_img_lab.place_forget()
        if type_add == 'folder' and name_fol:
            if os.path.exists(name_fol):
                warn('Папка с таким названием уже существует')
            else:
                folder = tk.Button(main_root, text=name_fol, width=460, background='#222123', foreground='#D1D1D1',
                                   relief=tk.FLAT, activebackground='White', image=folder_white_img, compound=tk.LEFT,
                                   padx=10, anchor='w', height=15)
                folder.bind('<Button-1>', lambda event: fold(event))
                folder.bind('<Enter>', lambda event, picture=folder_black_img: add_anim(event, picture, 'change'))
                folder.bind('<Leave>', lambda event, picture=folder_white_img: add_anim(event, picture, 'reset'))
                folder.place(x=5, y=dist)
                dist += 24
                add_root.destroy()
                os.mkdir(name_fol)
                folders_files[name_fol] = []
        elif type_add == 'write':
            write_title = title.get()
            if os.path.exists(f'{write_title}.txt'):
                warn('Запись с таким названием уже существует')
            else:
                write_but = tk.Button(main_root, text=write_title, width=460, background='#222123',
                                      foreground='#D1D1D1',
                                      relief=tk.FLAT, activebackground='White', image=write_white_img,
                                      compound=tk.LEFT,
                                      padx=10, anchor='w', height=15)
                write_but.bind('<Button-1>', lambda event: write(event))
                write_but.bind('<Enter>', lambda event, picture=write_black_img: add_anim(event, picture, 'change'))
                write_but.bind('<Leave>', lambda event, picture=write_white_img: add_anim(event, picture, 'reset'))
                write_but.place(x=5, y=dist)
                dist += 24
                if type_write == 'enter':
                    login_get = login.get()
                    password_get = password.get()
                    add_root.destroy()
                    with open(f'{write_title}.txt', 'w') as f:
                        f.write(f'{login_get}\n{password_get}')
                    folders_files[write_title] = {write_title: [login_get, password_get]}
                elif type_write == 'pay_card':
                    card_number_get = card_number.get()
                    pin_get = pin.get()
                    cvv_get = cvv.get()
                    term_get = term.get()
                    add_root.destroy()
                    with open(f'{write_title}.txt', 'w') as f:
                        f.write(f'{card_number_get}\n{pin_get}\n{cvv_get}\n{term_get}')
                    folders_files[write_title] = {write_title: [card_number_get, pin_get, cvv_get, term_get]}
        with open('hierarchy.bin', 'wb') as directory:
            pickle.dump(folders_files, directory)

    def disabled_all(e):
        for widget, text in write_widgets.items():
            if not widget.get():
                widget.insert(0, text)
                widget['state'] = 'disabled'
        enter.place_forget()
        pay_card.place_forget()

    def add_wr():
        nonlocal type_add
        add_root.geometry('195x175+560+210')
        types_write_lab['text'] = 'Вход'
        write_but['bg'] = '#363636'
        folder_but['bg'] = '#222123'
        name_fold.place_forget()
        ok_but.place(x=130, y=145)
        close_but.place(x=65, y=145)
        title.place(x=5, y=65)
        login.place(x=5, y=90)
        password.place(x=5, y=115)
        types_write_lab.place(x=5, y=35)
        types_write_but.place(x=70, y=35)
        type_add = 'write'

    def add_folder():
        nonlocal type_add
        add_root.geometry('195x103+560+210')
        write_but['bg'] = '#222123'
        folder_but['bg'] = '#363636'
        title.place_forget()
        types_write_lab.place_forget()
        types_write_but.place_forget()
        login.place_forget()
        password.place_forget()
        pin.place_forget()
        card_number.place_forget()
        cvv.place_forget()
        term.place_forget()
        ok_but.place(x=130, y=70)
        close_but.place(x=65, y=70)
        name_fold.place(x=5, y=40)
        type_add = 'folder'

    def types_write_unlock(e=None):
        if enter.winfo_viewable():
            enter.place_forget()
            pay_card.place_forget()
        else:
            enter.place(x=5, y=57)
            pay_card.place(x=5, y=78)

    def enter_type():
        nonlocal type_write
        add_root.geometry('195x175+560+210')
        types_write_lab['text'] = 'Вход'
        enter.place_forget()
        pay_card.place_forget()
        card_number.place_forget()
        pin.place_forget()
        cvv.place_forget()
        term.place_forget()
        login.place(x=5, y=90)
        password.place(x=5, y=115)
        ok_but.place(x=130, y=145)
        close_but.place(x=65, y=145)
        type_write = 'enter'

    def pay_card_type():
        nonlocal type_write
        add_root.geometry('195x200+560+210')
        types_write_lab['text'] = 'Карта'
        enter.place_forget()
        pay_card.place_forget()
        login.place_forget()
        password.place_forget()
        card_number.place(x=5, y=90)
        cvv.place(x=100, y=115)
        term.place(x=5, y=115)
        pin.place(x=5, y=140)
        ok_but.place(x=130, y=170)
        close_but.place(x=65, y=170)
        type_write = 'pay_card'

    add_root.geometry('170x120+410+210')
    add_root.title('Добавить')

    background = tk.Frame(add_root, height=250, width=480, background='#363636')
    background.place(relheight=1, relwidth=1)
    background.bind('<Button-1>', disabled_all)

    folder_but = tk.Button(add_root, background='#363636', foreground='White', text='Папка', width=7, relief=tk.FLAT,
                           command=add_folder, activebackground='#363636', activeforeground='White')
    folder_but.place(x=0, y=0)
    write_but = tk.Button(add_root, background='#222123', foreground='White', text='Запись', width=7, relief=tk.FLAT,
                          command=add_wr, activebackground='#363636', activeforeground='White')
    write_but.place(x=59, y=0)

    ok_but = tk.Button(add_root, background='#222123', foreground='White', text='ок', width=7, relief=tk.FLAT,
                       command=ok,
                       state='disabled', activeforeground='White', activebackground='Black')

    close_but = tk.Button(add_root, background='#222123', foreground='White', text='отмена', width=7, relief=tk.FLAT,
                          activeforeground='White', activebackground='Black')

    name_fold = tk.Entry(add_root, background='#222123', state='disabled',
                         disabledforeground='LightGrey', disabledbackground='#222123', foreground='White',
                         insertbackground='White', width=30, relief=tk.FLAT)
    name_fold.place(x=5, y=50)
    name_fold.bind('<Return>', ok)

    # поля в разделе добавить запись

    title = tk.Entry(add_root, background='#222123', foreground='White',
                     disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                     insertbackground='White', width=30, relief=tk.FLAT)

    login = tk.Entry(add_root, background='#222123', foreground='White',
                     disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                     insertbackground='White', width=30, relief=tk.FLAT)

    password = tk.Entry(add_root, background='#222123', foreground='White',
                        disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                        insertbackground='White', width=30, relief=tk.FLAT)

    card_number = tk.Entry(add_root, background='#222123', foreground='White',
                           disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                           insertbackground='White', width=30, relief=tk.FLAT)

    pin = tk.Entry(add_root, background='#222123', foreground='White',
                   disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                   insertbackground='White', width=30, relief=tk.FLAT)

    cvv = tk.Entry(add_root, background='#222123', foreground='White',
                   disabledforeground='LightGrey', disabledbackground='#222123', state='disabled',
                   insertbackground='White', width=14, relief=tk.FLAT)

    term = tk.Entry(add_root, background='#222123', foreground='White', disabledforeground='LightGrey',
                    disabledbackground='#222123', state='disabled', insertbackground='White', width=14, relief=tk.FLAT)

    # дальше не поля

    types_write_lab = tk.Label(add_root, text='Вход', width=10, background='#222123', foreground='White')
    types_write_lab.bind('<Button-1>', types_write_unlock)

    types_write_but = tk.Button(add_root, image=arrow_img, background='#222123', relief=tk.FLAT,
                                activebackground='Black',
                                width=15, height=15, command=types_write_unlock)

    enter = tk.Button(add_root, image=enter_white_img, compound=tk.LEFT, width=60, background='#222123', relief=tk.FLAT,
                      activebackground='White', text='Вход', foreground='White', activeforeground='Black', padx=10,
                      anchor='w', height=13, command=enter_type)

    enter.bind('<Enter>', lambda event, picture=enter_black_img: add_anim(event, picture, 'change'))
    enter.bind('<Leave>', lambda event, picture=enter_white_img: add_anim(event, picture, 'reset'))

    pay_card = tk.Button(add_root, image=card_white_img, compound=tk.LEFT, width=60, background='#222123',
                         relief=tk.FLAT,
                         activebackground='White', text='Карта', foreground='White', activeforeground='Black',
                         padx=10, anchor='w', height=13, command=pay_card_type)

    pay_card.bind('<Enter>', lambda event, picture=card_black_img: add_anim(event, picture, 'change'))
    pay_card.bind('<Leave>', lambda event, picture=card_white_img: add_anim(event, picture, 'reset'))

    write_widgets = {name_fold: 'Название папки', title: 'Название', login: 'Логин', password: 'Пароль',
                     card_number: 'Номер карты', pin: 'ПИН-код', cvv: 'CVV-код', term: 'срок(мм/гг)'}

    for w in write_widgets:
        w.bind('<Button-1>', lambda event, widget=w, text=write_widgets[w]: normal(event, widget, text))
        w.bind('<KeyRelease>', lambda event, widget=w, text=write_widgets[w]: normal(event, widget, text))
        text_wid = tk.StringVar()
        text_wid.set(write_widgets[w])
        w['textvariable'] = text_wid

    add_folder()


add_wr_but = tk.Button(main_root, compound=tk.LEFT, padx=10, anchor='w', width=35,
                       relief=tk.FLAT, background='#222123', activebackground='#222123',
                       foreground='White', command=add, image=add_white_img)
add_wr_but.place(x=450, y=252)
add_wr_but.bind('<Enter>', lambda event, picture=add_black_img: add_anim(event, picture))
add_wr_but.bind('<Leave>', lambda event, picture=add_white_img: add_anim(event, picture))

main()

main_root.mainloop()
