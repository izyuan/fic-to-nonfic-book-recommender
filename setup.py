import numpy as np
import pandas as pd
df = pd.read_csv("filesforbuilding/data\demo.csv") #remind me to change index into book title
similarity_matrix = np.load("filesforbuilding/arrays/combined_cosine_sim.npy")

def get_genre_specific_recommendations(title, similarity_matrix, df, top_n=10):
    idx = df.index.get_loc(title)
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # fetching the top 50 scores
    sim_scores = sim_scores[1:top_n*50]  
    fiction_recommendations = []
    nonfiction_recommendations = []
    
    for book_idx, score in sim_scores: #going through and appending for each recommendation
        if len(fiction_recommendations) < top_n and df.iloc[book_idx]['Genre1'] == 'Fiction':
            fiction_recommendations.append(df.iloc[book_idx].name)
        elif len(nonfiction_recommendations) < top_n and df.iloc[book_idx]['Genre1'] == 'Non-Fiction':
            nonfiction_recommendations.append(df.iloc[book_idx].name)
        if len(fiction_recommendations) == top_n and len(nonfiction_recommendations) == top_n:
            break
    
    return fiction_recommendations, nonfiction_recommendations

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sv_ttk

if 1 in df.index: 
    df.set_index('Book Title', inplace=True)

class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(font=("Times New Roman", 12))
        self.book_titles = sorted(kwargs.get('values', []))  # List of book titles
        self._completion_list = self.book_titles
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self._hits = []

    def handle_keyrelease(self, event):
        if event.keysym in ["BackSpace", "Left", "Right", "Return"]:
            self._update_autocomplete()
        else:
            self.after(13, self._update_autocomplete)

    def _update_autocomplete(self): #allows us to search for a book
        typed = self.get()
        if typed == '':
            self._hits = self._completion_list
        else:
            self._hits = [title for title in self._completion_list if typed.lower() in title.lower()]
        if self._hits:
            self['values'] = self._hits
        else:
            self['values'] = self._completion_list

def show_synopsis(title): #creating a dark themed synopsis window :DDD
    synopsis = df.loc[title]["Raw Synopsis"]
    synopsis_window = tk.Toplevel(root)
    synopsis_window.title(title)
    sv_ttk.set_theme("dark")
    synopsis_window.configure(background='#333333')
    synopsis_label = tk.Label(synopsis_window, text=synopsis, fg="white", bg="#333333", wraplength=400)
    synopsis_label.config(font=("Times New Roman", 12)) 
    synopsis_label.pack(padx=20, pady=20)
    
    close_btn = ttk.Button(synopsis_window, text="Close", command=synopsis_window.destroy)
    close_btn.pack(pady=10)

def update_recommendations(event):
    selected_book = book_var.get()
    fiction_recommendations, nonfiction_recommendations = get_genre_specific_recommendations(selected_book, similarity_matrix, df)
    # Clear existing entries in the treeview
    for i in recommendation_tree.get_children():
        recommendation_tree.delete(i)
    # Determine the shorter length to prevent 'IndexError'
    min_length = min(len(fiction_recommendations), len(nonfiction_recommendations))
    # Insert recommendations up to the shorter of the two lists
    for i in range(min_length):
        recommendation_tree.insert("", "end", values=(fiction_recommendations[i], nonfiction_recommendations[i]))

# Tkinter window setup
root = tk.Tk()
sv_ttk.set_theme("dark")
root.title("Book Recommendation System")

style = ttk.Style()
style.configure("Custom.Treeview", font=('Times New Roman', 12))

book_var = tk.StringVar()
book_titles = df.index.tolist()

book_dropdown = AutocompleteCombobox(root, textvariable=book_var, values=book_titles)
book_dropdown.grid(row=0, column=0, padx=10, pady=10)
book_dropdown.bind('<<ComboboxSelected>>', update_recommendations)

# Set up treeview, configuring the size
root.minsize(800, 300)  
recommendation_tree = ttk.Treeview(root, style="Custom.Treeview" , height=10)
recommendation_tree.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
recommendation_tree['columns'] = ('Fiction', 'Nonfiction')
recommendation_tree.heading('Fiction', text='Fiction')
recommendation_tree.heading('Nonfiction', text='Nonfiction')
recommendation_tree.column('#0', width=0, stretch=tk.NO)
recommendation_tree.heading('#0', text='')
recommendation_tree.column('Fiction', stretch=tk.YES, width=200)
recommendation_tree.column('Nonfiction', stretch=tk.YES, width=200)

# Bdouble click to show synopsis
def on_double_click(event):
    region = event.widget.identify_region(event.x, event.y)
    if region != "cell":
        return  # Exit if the click was not on a cell

    #calculate where the mouse is relative 
    column = event.widget.identify_column(event.x)
    item_id = event.widget.selection()[0]
    item_values = event.widget.item(item_id, 'values')

    if column == '#1':  
        title = item_values[0]  
    elif column == '#2': 
        title = item_values[1]  
    show_synopsis(title)

recommendation_tree.bind("<Double-1>", on_double_click)


root.mainloop()