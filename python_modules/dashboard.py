import tkinter as tk
from tkinter import ttk, messagebox
from .db_connector import DB
from .utils import timestamp

DBI = DB()

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Linux Security Guardian - Dashboard')
        self.geometry('800x480')
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=('timestamp','type','details','severity'), show='headings')
        self.tree.heading('timestamp', text='Timestamp')
        self.tree.heading('type', text='Type')
        self.tree.heading('details', text='Details')
        self.tree.heading('severity', text='Severity')
        self.tree.pack(fill='both', expand=True)

        frm = ttk.Frame(self)
        frm.pack(fill='x')
        ttk.Button(frm, text='Refresh', command=self.refresh).pack(side='left')
        ttk.Button(frm, text='Clear Logs', command=self.clear_logs).pack(side='left')
        ttk.Button(frm, text='Manage Whitelist', command=self.manage_whitelist).pack(side='left')

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = DBI.fetch_recent(200)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def clear_logs(self):
        if messagebox.askyesno('Confirm','Delete all events?'):
            c = DBI.conn.cursor()
            c.execute('DELETE FROM events')
            DBI.conn.commit()
            self.refresh()

    def manage_whitelist(self):
        WhitelistWindow(self)

class WhitelistWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Whitelist Manager')
        self.geometry('600x300')
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=('id','name','path'), show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('path', text='Path')
        self.tree.pack(fill='both', expand=True)

        frm = ttk.Frame(self)
        frm.pack(fill='x')
        ttk.Button(frm, text='Add', command=self.add_entry).pack(side='left')
        ttk.Button(frm, text='Delete', command=self.delete_entry).pack(side='left')

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        c = DBI.conn.cursor()
        c.execute('SELECT id,name,path FROM whitelist')
        for row in c.fetchall():
            self.tree.insert('', 'end', values=row)

    def add_entry(self):
        def do_add():
            name = e1.get().strip()
            path = e2.get().strip()
            if name and path:
                c = DBI.conn.cursor()
                c.execute('INSERT INTO whitelist (name,path) VALUES (?,?)', (name,path))
                DBI.conn.commit()
                top.destroy(); self.refresh()
        top = tk.Toplevel(self)
        ttk.Label(top, text='Name').pack(); e1 = ttk.Entry(top); e1.pack()
        ttk.Label(top, text='Path').pack(); e2 = ttk.Entry(top); e2.pack()
        ttk.Button(top, text='Add', command=do_add).pack()

    def delete_entry(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        idv = item['values'][0]
        c = DBI.conn.cursor()
        c.execute('DELETE FROM whitelist WHERE id=?', (idv,))
        DBI.conn.commit()
        self.refresh()

if __name__ == '__main__':
    Dashboard().mainloop()
