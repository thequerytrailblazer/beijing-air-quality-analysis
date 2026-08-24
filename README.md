# Beijing Air Quality Analysis Dashboard

Dashboard interaktif berbasis Streamlit untuk menganalisis tren konsentrasi polutan PM2.5 serta hubungannya dengan parameter cuaca di Kota Beijing periode 2013–2017.

# Dataset

Data ini diperoleh dari dataset [HTI](https://github.com/marceloreis/HTI) oleh Marceloreis.

## Setup Environment & Instalasi

1. Clone repositori ini atau ekstrak folder proyek.
2. Buka terminal/command prompt di direktori proyek.
3. (Opsional) Buat dan aktifkan virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Windows: venv\Scripts\activate
   ```
4. Install seluruh dependensi library:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan Dashboard

Jalankan perintah berikut di terminal dari root folder proyek:

```bash
streamlit run dashboard/dashboard.py
```