import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import random
from tkinter import font

class FilmTavsiyeRobotu:
    def __init__(self, root):
        self.root = root
        self.root.title("Film Tavsiye Robotu")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        # Ana scrollable frame
        canvas = tk.Canvas(root, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Verileri yükle
        self.load_data()
        
        # Ana çerçeveyi oluştur
        main_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_font = font.Font(family="Arial", size=18, weight="bold")
        title_label = tk.Label(main_frame, text="Film Tavsiye Robotu", font=title_font, bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=(0, 20))
        
        # Form elemanları
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.X, pady=10)
        
        # Yaş seçimi
        age_frame = tk.LabelFrame(form_frame, text="Yaşınız", bg="#f0f0f0", padx=10, pady=10)
        age_frame.pack(fill=tk.X, pady=10)
        
        self.age_var = tk.StringVar(value="13+")
        age_options = ["genel", "13+", "16+", "18+"]
        
        for option in age_options:
            rb = tk.Radiobutton(age_frame, text=option, variable=self.age_var, value=option, bg="#f0f0f0")
            rb.pack(side=tk.LEFT, padx=10)
        
        # Film türleri
        genre_frame = tk.LabelFrame(form_frame, text="Film Türleri", bg="#f0f0f0", padx=10, pady=10)
        genre_frame.pack(fill=tk.X, pady=10)
        
        # Tüm film türlerini JSON dosyasından almak
        all_genres = set()
        for movie in self.movies_data["movies"]:
            for genre in movie["genre"]:
                all_genres.add(genre)
        
        all_genres = sorted(list(all_genres))
        
        # Film türü seçimlerini düzenle - daha görünür checkboxlar
        self.genre_vars = {}
        genre_col = 0
        genre_row = 0
        
        for genre in all_genres:
            self.genre_vars[genre] = tk.BooleanVar()
            frame = tk.Frame(genre_frame, bg="#f0f0f0")
            frame.grid(row=genre_row, column=genre_col, sticky="w", padx=5, pady=3)
            
            cb = tk.Checkbutton(
                frame, 
                text=genre, 
                variable=self.genre_vars[genre], 
                bg="#f0f0f0",
                font=("Arial", 11)
            )
            cb.pack(side=tk.LEFT)
            
            genre_col += 1
            if genre_col > 2:  # 3 sütun kullan - daha geniş görünüm için
                genre_col = 0
                genre_row += 1
        
        # Anahtar kelimeler
        keywords_frame = tk.LabelFrame(form_frame, text="İlgi Alanları", bg="#f0f0f0", padx=10, pady=10)
        keywords_frame.pack(fill=tk.X, pady=10)
        
        # Tüm anahtar kelimeleri JSON dosyasından almak
        all_keywords = set()
        for movie in self.movies_data["movies"]:
            for keyword in movie["keywords"]:
                all_keywords.add(keyword)
        
        all_keywords = sorted(list(all_keywords))
        
        # Anahtar kelime seçimlerini düzenle - daha görünür checkboxlar
        self.keyword_vars = {}
        keyword_col = 0
        keyword_row = 0
        
        for keyword in all_keywords:
            self.keyword_vars[keyword] = tk.BooleanVar()
            frame = tk.Frame(keywords_frame, bg="#f0f0f0")
            frame.grid(row=keyword_row, column=keyword_col, sticky="w", padx=5, pady=3)
            
            cb = tk.Checkbutton(
                frame, 
                text=keyword, 
                variable=self.keyword_vars[keyword], 
                bg="#f0f0f0",
                font=("Arial", 11)
            )
            cb.pack(side=tk.LEFT)
            
            keyword_col += 1
            if keyword_col > 2:  # 3 sütun kullan - daha geniş görünüm için
                keyword_col = 0
                keyword_row += 1
        
        # Öneri butonu - daha görünür bir yere koyalım
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=20, fill=tk.X)
        
        recommend_button = tk.Button(
            button_frame, 
            text="FİLM ÖNER", 
            command=self.recommend_movie,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=12,
            relief=tk.RAISED,
            borderwidth=3
        )
        recommend_button.pack(pady=10, padx=100, fill=tk.X)
        
        # Butonun görünür olduğuna dair bilgilendirme
        button_info = tk.Label(
            button_frame,
            text="👆 Yukarıdaki butona tıklayarak film önerisi alabilirsiniz 👆",
            font=("Arial", 10, "italic"),
            bg="#f0f0f0",
            fg="#555555"
        )
        button_info.pack(pady=5)
        
        # Sonuç alanı
        self.result_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Sonuç başlığı
        self.result_title = tk.Label(
            self.result_frame, 
            text="", 
            font=("Arial", 14, "bold"), 
            bg="#f0f0f0",
            fg="#333333"
        )
        self.result_title.pack(pady=(0, 10))
        
        # Sonuç bilgileri
        self.result_info = tk.Label(
            self.result_frame, 
            text="", 
            font=("Arial", 12), 
            bg="#f0f0f0",
            fg="#333333",
            justify=tk.LEFT,
            wraplength=700
        )
        self.result_info.pack(pady=5)
        
        # Filmin açıklaması
        self.result_description = tk.Label(
            self.result_frame, 
            text="", 
            font=("Arial", 12), 
            bg="#f0f0f0",
            fg="#333333",
            justify=tk.LEFT,
            wraplength=700
        )
        self.result_description.pack(pady=5)
        
    def load_data(self):
        try:
            with open("movies.json", "r", encoding="utf-8") as file:
                self.movies_data = json.load(file)
        except Exception as e:
            messagebox.showerror("Hata", f"Film verileri yüklenemedi: {e}")
            self.movies_data = {"movies": []}
    
    def recommend_movie(self):
        # Kullanıcı seçimlerini al
        selected_age = self.age_var.get()
        selected_genres = [genre for genre, var in self.genre_vars.items() if var.get()]
        selected_keywords = [keyword for keyword, var in self.keyword_vars.items() if var.get()]
        
        # Hiçbir tür veya anahtar kelime seçilmediyse uyarı ver
        if not selected_genres and not selected_keywords:
            messagebox.showwarning("Uyarı", "Lütfen en az bir film türü veya ilgi alanı seçiniz!")
            return
        
        # Yaşa uygun filmleri filtrele
        age_ratings = {"genel": 0, "13+": 13, "16+": 16, "18+": 18}
        selected_age_value = age_ratings[selected_age]
        
        suitable_movies = []
        
        for movie in self.movies_data["movies"]:
            movie_age_value = age_ratings.get(movie["ageRating"], 0)
            
            # Yaş kontrolü
            if movie_age_value > selected_age_value:
                continue
            
            # Puan hesapla (film ne kadar iyi eşleşiyor)
            match_score = 0
            
            # Tür eşleşmesi
            for genre in movie["genre"]:
                if genre in selected_genres:
                    match_score += 5
            
            # Anahtar kelime eşleşmesi
            for keyword in movie["keywords"]:
                if keyword in selected_keywords:
                    match_score += 3
            
            # Eğer hiç eşleşme yoksa filmi ekleme
            if match_score > 0:
                suitable_movies.append((movie, match_score))
        
        # Uygun film yoksa bilgilendir
        if not suitable_movies:
            self.result_title.config(text="Uygun film bulunamadı!")
            self.result_info.config(text="Lütfen farklı kriterler seçerek tekrar deneyin.")
            self.result_description.config(text="")
            return
        
        # En iyi eşleşen filmleri bul
        suitable_movies.sort(key=lambda x: (x[1], x[0]["rating"]), reverse=True)
        
        # En yüksek puanlı filmlerden rastgele birini seç
        top_score = suitable_movies[0][1]
        top_movies = [movie for movie, score in suitable_movies if score >= top_score * 0.8]
        
        recommended_movie = random.choice(top_movies)
        
        # Sonucu göster
        self.result_title.config(text=recommended_movie["title"])
        
        # Film bilgilerini düzenle
        info_text = f"Yönetmen: {recommended_movie['director']}\n"
        info_text += f"Yıl: {recommended_movie['year']}\n"
        info_text += f"Tür: {', '.join(recommended_movie['genre'])}\n"
        info_text += f"Puan: {recommended_movie['rating']}/10\n"
        info_text += f"Yaş Sınırı: {recommended_movie['ageRating']}"
        
        self.result_info.config(text=info_text)
        self.result_description.config(text=f"Film Hakkında: {recommended_movie['description']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FilmTavsiyeRobotu(root)
    
    # Fare tekerleği ile kaydırma etkinleştirme
    def _on_mousewheel(event):
        canvas = event.widget
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    root.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Başlangıçta kullanıcıya bilgi ver
    messagebox.showinfo("Hoş Geldiniz", "Film Tavsiye Robotu'na hoş geldiniz!\n\nLütfen form alanlarını doldurun ve 'FİLM ÖNER' butonuna tıklayın.\n\nButonu görmek için gerekirse sayfayı aşağı kaydırabilirsiniz.")
    
    root.mainloop()