import tkinter as tk
import speech_recognition as sr
import webbrowser
import os
import threading
import time
import requests
from gtts import gTTS
import pygame

recognizer = sr.Recognizer()

# API anahtarı aldıysanız burayı değiştirin.
API_KEY = "BURAYA_API_ANAHTARINIZI_YAZIN"

# pygame start
pygame.mixer.init()

import time


def seslendir(metin):
    pygame.mixer.stop()

    dosya_yolu = f"response_{time.time()}.mp3"

    tts = gTTS(text=metin, lang='tr', slow=False)
    tts.save(dosya_yolu)

    pygame.mixer.music.load(dosya_yolu)
    pygame.mixer.music.play()

    def dosya_sil():
        while pygame.mixer.music.get_busy():  # Çalma bitene kadar bekle
            time.sleep(0.1)
        pygame.mixer.music.unload()
        try:
            if os.path.exists(dosya_yolu):
                os.remove(dosya_yolu)
                print(f"Silindi: {dosya_yolu}")
        except Exception as e:
            print(f"Dosya silme hatası: {e}")

    threading.Thread(target=dosya_sil, daemon=True).start()



def surekli_dinle():
    def arka_planda_dinleme():
        while True:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                try:
                    text = recognizer.recognize_google(audio, language="tr-TR")
                    if "asistan" in text.lower():
                        durum_label.config(text="Komut bekleniyor...")
                        seslendir("Dinliyorum")
                        ses_dinle()
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    durum_label.config(text="API hatası.")
                    break

    threading.Thread(target=arka_planda_dinleme, daemon=True).start()

def ses_dinle():
    def arka_planda_ses_dinle():
        with sr.Microphone() as source:
            recognizer.pause_threshold = 1.0  # Duraksama eşiği ayarı
            recognizer.adjust_for_ambient_noise(source)
            durum_label.config(text="Lütfen konuşun...")
            window.update()
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio, language="tr-TR")
                durum_label.config(text=f"Siz: {text}")
                komut_analiz_et(text)
            except sr.UnknownValueError:
                durum_label.config(text="Ses anlaşılamadı.")
            except sr.RequestError:
                durum_label.config(text="API hatası.")

    threading.Thread(target=arka_planda_ses_dinle).start()

def komut_analiz_et(komut):
    if "Google'da ara" in komut:
        arama_terimi = komut.replace("Google'da ara", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={arama_terimi}")
        seslendir(f"Google'da arama yapılıyor: {arama_terimi}")
        durum_label.config(text=f"Google'da arama yapılıyor: {arama_terimi}")

    elif "kapan" in komut:
        seslendir("Uygulama kapanıyor.")
        window.destroy()

    elif "çöp kutusunu boşalt" in komut:
        try:
            os.system("powershell.exe -command \"Clear-RecycleBin -Force\"")
            seslendir("Çöp kutusu boşaltıldı.")
            durum_label.config(text="Çöp kutusu boşaltıldı.")
        except Exception as e:
            seslendir(f"Bir hata oluştu: {str(e)}")
            durum_label.config(text="Bir hata oluştu: " + str(e))

    elif "spotify'da" in komut and "aç" in komut:
        sarki_adi = komut.replace("spotify'da", "").replace("aç", "").strip()
        spotify_url = f"https://open.spotify.com/search/{sarki_adi.replace(' ', '%20')}"
        
        webbrowser.open(spotify_url)
        seslendir(f"Spotify'da aranıyor: {sarki_adi}")
        durum_label.config(text=f"Spotify'da aranıyor: {sarki_adi}")
       
        time.sleep(5)

    elif "kapat" in komut:
        uygulama_adi = komut.replace("kapat", "").strip()
        
        # Eğer program adı belirtilmişse
        if uygulama_adi:
            # Çalışan işlemleri listele
            output = os.popen('tasklist').read().lower()
            
            if f"{uygulama_adi}.exe" in output:
                # Belirtilen uygulamayı kapat
                os.system(f"taskkill /F /IM {uygulama_adi}.exe")
                seslendir(f"{uygulama_adi} kapatıldı.")
                durum_label.config(text=f"{uygulama_adi} kapatıldı.")
            else:
                seslendir(f"{uygulama_adi} çalışmıyor.")
                durum_label.config(text=f"{uygulama_adi} çalışmıyor.")
        else:
            seslendir("Lütfen bir program adı belirtin.")
            durum_label.config(text="Lütfen bir program adı belirtin.")

    elif "hava durumu" in komut:
        # Şehir adı al
        sehir = komut.replace("hava durumu", "").strip()

        if sehir:
            # WeatherAPI'den hava durumu bilgisi al
            hava_durumu(sehir)
        else:
            seslendir("Lütfen bir şehir adı belirtin.")
            durum_label.config(text="Lütfen bir şehir adı belirtin.")

    elif "masaüstünde" in komut and "aç" in komut:
        uygulama_adi = komut.split("masaüstünde")[1].split("aç")[0].strip()
        masaustu_yolu = os.path.join(os.path.expanduser("~"), "OneDrive", "Masaüstü")
        
        dosya_bulundu = False
        for dosya in os.listdir(masaustu_yolu):
            if uygulama_adi.lower() in dosya.lower() and dosya.endswith(".lnk"):
                os.startfile(os.path.join(masaustu_yolu, dosya)) 
                seslendir(f"{uygulama_adi} açılıyor.")
                durum_label.config(text=f"{uygulama_adi} açılıyor.")
                dosya_bulundu = True
                break

        if not dosya_bulundu:
            seslendir(f"{uygulama_adi} masaüstünde bulunamadı.")
            durum_label.config(text=f"{uygulama_adi} masaüstünde bulunamadı.")
    else:
        seslendir("Komut anlaşılamadı.")
        durum_label.config(text="Komut anlaşılamadı.")

# API
def hava_durumu(sehir):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={sehir}&lang=tr"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'current' in data:
            # Bilgileri çek
            sıcaklık = data['current']['temp_c']
            hava = data['current']['condition']['text']
            seslendir(f"{sehir} için hava durumu: {sıcaklık}°C, {hava}")
            durum_label.config(text=f"{sehir} için hava durumu: {sıcaklık}°C, {hava}")
        else:
            seslendir("Hava durumu bilgisi alınamadı.")
            durum_label.config(text="Hava durumu bilgisi alınamadı.")
    else:
        seslendir("Hava durumu servisi ile bağlantı kurulamadı.")
        durum_label.config(text="Hava durumu servisi ile bağlantı kurulamadı.")

# GUI
window = tk.Tk()
window.title("Sesli Asistan")
window.geometry("400x200")

durum_label = tk.Label(window, text="Sesli komutlar için 'asistan' deyin.", wraplength=300)
durum_label.pack(pady=20)

surekli_dinle()

window.mainloop()
      
