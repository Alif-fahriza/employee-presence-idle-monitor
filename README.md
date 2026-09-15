# 👁️ Employee Presence & Idle-Time Monitor

> Project Computer Vision berbasis Python + OpenCV yang memantau **kehidupan karyawan** melalui webcam secara *real-time*.
> Mendeteksi kehadiran wajah, mengukur **total waktu kehadiran**, dan menampilkan status **PRESENT / AWAY** dengan *grace period* — dilengkapi HUD interaktif di layar.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?logo=opencv&logoColor=white)
![DNN](https://img.shields.io/badge/DNN-Face%20Detector-4CAF50?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?logo=opensource&logoColor=white)

---

## 📖 Tentang Project

**Employee Presence & Idle-Time Monitor** adalah aplikasi *desktop* berbasis Computer Vision yang memantau kehadiran karyawan menggunakan **deteksi wajah** dari webcam.

Program ini menggunakan **OpenCV DNN (ResNet-SSD)** sebagai detektor utama, dengan **fallback ke Haar Cascade** jika model DNN belum tersedia — sehingga program tetap jalan meski tanpa download model terpisah.

Program ini cocok untuk:
- Monitoring kehadiran karyawan di ruang kerja
- Mengukur durasi kehadiran dalam sesi kerja
- Mempelajari dasar-dasar state machine dalam aplikasi Computer Vision

---

## ✨ Fitur

### ✅ Deteksi Wajah Real-time

| Fitur | Keterangan |
|-------|------------|
| **OpenCV DNN (ResNet-SSD)** | Detektor utama — akurat, mendeteksi 1+ wajah |
| **Haar Cascade Fallback** | Otomatis aktif jika model DNN belum ter-download |
| **Auto-Download Model** | Model (~10 MB) di-download otomatis saat pertama kali dijalankan |
| **Confidence Threshold** | Hanya mendeteksi wajah dengan confidence ≥ 65% |
| **Bounding Box + Label** | Menggambar kotak wajah + label "Face detected" |

### ✅ State Machine PRESENT / AWAY

| Fitur | Keterangan |
|-------|------------|
| **State PRESENT** | Wajah terdeteksi — user dianggap hadir |
| **State AWAY** | Wajah tidak terdeteksi — user dianggap meninggalkan ruangan |
| **Grace Period (5 detik)** | Status tidak langsung berubah — tunggu 5 detik barulah AWAY. Mencegah false positive (misal: user menoleh sebentar) |
| **State Transition** | PRESENT → AWAY: setelah grace period. AWAY → PRESENT: segera saat wajah terdeteksi |

### ✅ Timer & Dashboard

| Fitur | Keterangan |
|-------|------------|
| **Session Timer** | Timer sesi saat ini (PRESENT atau AWAY) |
| **Total Presence Time** | Akumulasi total waktu karyawan hadir (format `HH:MM:SS`) |
| **HUD Overlay** | Panel semi-transparan di layar dengan semua informasi |
| **Wall Clock** | Jam sistem yang terlihat (pojok kanan atas) |
| **Status Badge** | Badge besar "PRESENT" (hijau) atau "AWAY" (merah) |

### ✅ Antarmuka Pengguna

| Fitur | Keterangan |
|-------|------------|
| **Bounding Box Wajah** | Kotak deteksi wajah dengan warna sesuai status |
| **Label Atas Wajah** | "Face detected" berwarna di atas kotak bounding box |
| **Total Presence Badge** | Badge kecil dengan total waktu kehadiran menempel pada bounding box |
| **Grace Countdown** | Menampilkan sisa waktu grace period saat user mulai menghadap pergi |
| **Panel HUD Bawah** | Panel gelap di bagian bawah layar dengan semua informasi |

---

## 📸 Visual

> Program menampilkan webcam dengan overlay HUD yang menunjukkan:
> - Wajah terdeteksi (bounding box hijau + label)
> - Status "PRESENT" (badge hijau)
> - Timer sesi & total kehadiran
> - Jam sistem
> - Sisa waktu grace period (jika sedang tunggu)

---

## 🛠️ Teknologi

| Teknologi | Kegunaan |
|-----------|----------|
| **[Python 3.11+](https://www.python.org/)** | Bahasa pemrograman utama |
| **[OpenCV](https://opencv.org/)** | Computer Vision: akses kamera, DNN inference, rendering HUD |
| **[OpenCV DNN](https://docs.opencv.org/4.x/d6/d0f/group__dnn__module.html)** | ResNet-SSD face detector (model Caffe) |
| **[Haar Cascade](https://docs.opencv.org/4.x/db/d28/tutorial_table_of_content_obj_det.html)** | Fallback face detector bawaan OpenCV |

---

## 📁 Struktur Project

```
employee-presence-idle-monitor/
├── main.py              # Entry point — state machine & loop utama
├── config.py            # Semua konstanta & konfigurasi
├── detector.py          # Face detector (DNN + Haar fallback)
├── hud.py               # HUD overlay (rendering & tampilan)
├── run.bat              # Script batch Windows
├── deploy.prototxt      # Arsitektur model Caffe SSD
├── res10_300x300_ssd_iter_140000.caffemodel  # Model AI (10.6 MB)
└── .gitignore           # Exclude __pycache__, venv, dll.
```

### 📂 Penjelasan File

| File | Fungsi |
|------|--------|
| `main.py` | Program utama — state machine PRESENT/AWAY, akumulasi waktu, loop webcam |
| `config.py` | Semua konfigurasi: threshold, path model, warna, grace period, dll. — ubah di sini tanpa sentuh file lain |
| `detector.py` | Load & jalankan face detector: prioritas DNN (ResNet-SSD), fallback Haar Cascade |
| `hud.py` | Menggambar overlay: bounding box wajah, badge status, timer, total presence, jam sistem, grace countdown |
| `run.bat` | Script Windows untuk menjalankan program |
| `deploy.prototxt` | File arsitektur Caffe (dibuat oleh OpenCV) — menunjukkan struktur model |
| `res10_300x300_ssd_iter_140000.caffemodel` | Model Caffe SSD terlatih — berat ~10.6 MB |

---

## 🚀 Instalasi & Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/Alif-fahriza/employee-presence-idle-monitor.git
cd employee-presence-idle-monitor
```

### 2. Install Dependencies

```bash
pip install opencv-python
```

> Hanya membutuhkan **opencv-python** — library Computer Vision terpopuler.

### 3. Jalankan Program

```bash
python main.py
```

Atau gunakan script batch (Windows):

```bash
run.bat
```

> **Catatan:** Saat pertama kali dijalankan, model DNN (~10 MB) akan di-download otomatis dari GitHub OpenCV.

### 4. Kontrol Program

| Tombol | Fungsi |
|--------|--------|
| **`Q`** | Keluar dari program |

---

## 🤖 Cara Kerja Deteksi

### Alur State Machine

```
[AWAY] ──(wajah ditemukan)──► [PRESENT]
  ▲                              │
  │          (grace period       │
  │           habis +            │
  │           wajah hilang)      │
  └──────────────────────────────┘
```

| Transisi | Kondisi |
|----------|---------|
| **AWAY → PRESENT** | Wajah terdeteksi (immediately) |
| **PRESENT → AWAY** | Wajah tidak terdeteksi ≥ GRACE_PERIOD_SEC (5 detik) |

### Detektor — Prioritas & Fallback

```
1. OpenCV DNN (ResNet-SSD)
   └── File: deploy.prototxt + res10_300x300_ssd_iter_140000.caffemodel
   └── Threshold: confidence ≥ 0.65
   └── Auto-download jika belum ada

2. Haar Cascade (fallback)
   └── File: haarcascade_frontalface_default.xml (bawaan OpenCV)
   └── ScaleFactor: 1.1, MinNeighbors: 5
```

---

## 🎨 Warna & Visual

| Elemen | Warna (BGR) | Arti |
|--------|-------------|------|
| **Status PRESENT** | `(50, 205, 50)` — Lime Green | Karyawan hadir |
| **Status AWAY** | `(60, 60, 220)` — Vivid Red | Karyawan tidak hadir |
| **Teks Utama** | `(255, 255, 255)` — White | Teks HUD |
| **Panel Latar** | `(20, 20, 20)` — Near Black | Semi-transparan 65% |

---

## ⚙️ Konfigurasi

Semua konfigurasi ada di **`config.py`**. Kamu bisa mengubahnya tanpa perlu sentuh file lain:

| Parameter | Nilai Default | Keterangan |
|-----------|---------------|------------|
| `CAMERA_INDEX` | `0` | Index webcam (0 = default) |
| `GRACE_PERIOD_SEC` | `5.0` | Detik sebelum PRESENT → AWAY |
| `DNN_CONFIDENCE` | `0.65` | Confidence minimum deteksi DNN |
| `MIN_FACE_SIZE` | `(60, 60)` | Ukuran minimum wajah (Haar fallback) |

---

## 👨‍💻 Developer

| | |
|---|---|
| **Nama** | Alif Fahriza |
| **Email** | aliffahriza70@gmail.com |
| **GitHub** | [@Alif-fahriza](https://github.com/Alif-fahriza) |

---

## 📄 Lisensi

Project ini menggunakan lisensi **MIT License** — bebas digunakan, dimodifikasi, dan didistribusikan untuk tujuan apapun.

---

## 🙏 Terima Kasih

- **[OpenCV](https://opencv.org/)** — Computer Vision library & pretrained models
- **[OpenCV DNN Samples](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)** — ResNet-SSD face detector model
- **Semua pihak yang telah berkontribusi pada ekosistem Computer Vision** 🙌

---

> 💡 **Tips:** Ikuti repository ini untuk update pengembangan selanjutnya.

⭐ **Jangan lupa beri star kalau project ini membantu!**
