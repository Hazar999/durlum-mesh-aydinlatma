# Durlum Mesh Seçim ve Aydınlatma Ön Hesap Aracı - V1

Bu prototip iki ana işi yapar:

1. RHOMBOS katalog verisine göre mesh/panel versiyonu ve sistem panel ölçüsü kontrolü.
2. Lümen yöntemiyle hızlı aydınlatma ön hesabı ve mesh alternatif karşılaştırması.

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Aydınlatma formülü

```text
E_ort = N × Lümen × UF × MF × T / Alan
```

- `UF`: kullanım faktörü
- `MF`: bakım faktörü
- `T`: mesh etkin ışık geçirgenliği

Katalogdaki `OA` açık alan oranıdır; doğrudan doğrulanmış ışık geçirgenliği değildir. V1 içinde yalnızca geçici yaklaşım olarak kullanılır. Kesin hesap için mesh/rengin/yönün/armatür mesafesinin ölçülmesi veya fotometrik simülasyonu gerekir.

## Sonraki aşama

- Durlum'un gerçek armatür lümen, güç ve IES/LDT verileri
- Mesh bazlı lux deneyleri ve ölçülmüş T katsayıları
- Renk ve Q-R yönü bazlı kalibrasyon
- Proje raporu/PDF çıktısı
- DIALux doğrulama alanları
