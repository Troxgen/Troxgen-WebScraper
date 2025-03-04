import os
import requests
from bs4 import BeautifulSoup
import hashlib

def sanitize_filename(name, max_length=50):
    """Dosya ve klasör adlarını temizle ve uzunluğu sınırla."""
    name = name.strip().replace(" ", "_").replace("/", "_").replace(":", "_").replace("|", "_")
    if len(name) > max_length:
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        name = name[:40] + "_" + hash_suffix
    return name

def create_folder(path):
    """Belirtilen dizini oluştur."""
    os.makedirs(path, exist_ok=True)

def download_file(url, folder, headers):
    """Belirtilen URL'deki dosyayı indir ve kaydet."""
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        file_path = os.path.join(folder, sanitize_filename(os.path.basename(url.split("?")[0])))
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Dosya kaydedildi: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Dosya indirirken hata oluştu ({url}): {e}")

def scrape_page(url, kategori_adi):
    """Belirtilen sayfadaki ürünleri tarar ve dosyaları indirir."""
    base_folder = f"urun_dokumanlari/{kategori_adi}"
    create_folder(base_folder)
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Web sayfasına erişirken hata oluştu: {e}")
        return

    for div in soup.find_all("div", class_="sbeyazback"):
        try:
            urun_adi = sanitize_filename(div.find("h2").text.strip())
            urun_folder = os.path.join(base_folder, urun_adi)
            create_folder(urun_folder)

            for img in div.find_all("img", class_="urunresim"):
                img_url = img.get("src")
                if img_url and not img_url.startswith("http"):
                    img_url = "https://example-site.com" + img_url
                download_file(img_url, urun_folder, headers)

            for pdf in div.find_all("a", href=True):
                pdf_url = pdf.get("href")
                if pdf_url.endswith(".pdf"):
                    if not pdf_url.startswith("http"):
                        pdf_url = "https://example-site.com" + pdf_url
                    download_file(pdf_url, urun_folder, headers)
        except Exception as e:
            print(f"Ürün işlenirken hata oluştu: {e}")

if __name__ == "__main__":
    link = input("Lütfen veri çekmek istediğiniz sayfanın linkini girin: ")
    kategori_adi = sanitize_filename(input("Lütfen kategori adını girin: "))
    scrape_page(link, kategori_adi)
