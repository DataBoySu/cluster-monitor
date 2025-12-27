## माईजीपीयू: लाइटवेट GPU प्रबंधन उपकरण

*माईजीपीयू: एक संक्षिप्त `nvidia-smi` वैरिएंट, एक सुंदर वेब डैशबोर्ड के साथ एक संक्षिप्त GPU प्रबंधन उपकरण।*

![लाइसेंस](https://img.shields.io/badge/लाइसेंस-MIT-blue.svg)
![पायथन](https://img.shields.io/badge/पायथन-3.10%2B-blue)
![संस्करण](https://img.shields.io/badge/संस्करण-1.2.3-blue)
![प्लेटफ़ॉर्म](https://img.shields.io/badge/प्लेटफ़ॉर्म-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## गैलरी

<details>

  <summary>
  वेब डैशबोर्ड
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>

</details>
<details>
  <summary>CLI</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <!-- अन्य CLI छवियाँ यहाँ जोड़ें -->
  </div>
</details>

### इसका उपयोग क्यों करें?

- **लाइटवेट**: न्यूनतम संसाधन पैरामीटर।
- **लचीला**: CLI उपकरण के रूप में चलाएँ या पूर्ण विशेषताओं वाला वेब डैशबोर्ड।
- **प्रशासक-केंद्रित**: **VRAM प्रवर्तन** (सीमाओं से अधिक उपयोग करने वाली प्रक्रियाओं को स्वचालित रूप से समाप्त करें) और **वॉचलिस्ट** शामिल हैं।
- **डेवलपर-अनुकूल**: जेएमएम (जेनेरिक मैट्रिक्स मल्टीप्लिकेशन) और कण भौतिकी जैसे तनाव परीक्षण और सिमुलेशन उपकरणों के साथ निर्मित।

---

## विशेषताएँ

- **रियल-टाइम मॉनिटरिंग**:
  - विस्तृत GPU मेट्रिक्स (उपयोग, VRAM, शक्ति, तापमान)।
  - सिस्टम मेट्रिक्स (CPU, RAM, आदि)।

- **प्रशासक और प्रवर्तन**:
  - **VRAM सीमाएँ**: प्रत्येक GPU के लिए VRAM उपयोग पर कठोर सीमाएँ सेट करें।
  - **स्वचालित समाप्ति**: प्रशासक के लिए VRAM नीतियों का उल्लंघन करने वाली प्रक्रियाओं को स्वचालित रूप से समाप्त करें।
  - **वॉचलिस्ट**: विशिष्ट PID या प्रक्रिया नामों की निगरानी करें।

- **तनाव परीक्षण और सिमुलेशन**:
  - **तनाव परीक्षण**: जेएमएम कार्यभारों के साथ कॉन्फ़िगरेबल GEMM तनाव परीक्षण।
  - **कण भौतिकी सिमुलेशन**: GPU लोड को दृश्य बनाने के लिए इंटरैक्टिव 3D कण भौतिकी सिमुलेशन।

---

## रोडमैप और भविष्य का काम

योगदान स्वागत है! मुख्य भविष्य के बिंदुओं को कवर करने के लिए:

- **बहु-GPU समर्थन**: एनवीएलिन टॉपोलॉजी के लिए उन्नत हैंडलिंग।
- **कंटेनराइजेशन**: आधिकारिक डॉकर समर्थन के लिए आसान तैनाती।
- **दूरस्थ पहुँच**: SSH टनलिंग एकीकरण और सुरक्षित दूरस्थ प्रबंधन।
- **प्लेटफ़ॉर्म-निरपेक्ष**:
  - [ ] लिनक्स समर्थन (यूबंटू/डेबियन फ़ोकस)।
  - [ ] एप्पल सिलिकॉन के लिए मॉनिटरिंग।
- **हार्डवेयर-अग्नेस्ट**:
  - [ ] AMD ROCm समर्थन।
  - [ ] इंटेल आर्क समर्थन।
- ~~**बहु-भाषा दस्तावेज़ीकरण**: सबसे लोकप्रिय GitHub भाषाओं का समर्थन।~~

[CONTRIBUTING.md](../CONTRIBUTING.md) देखें कि कैसे योगदान करें।

---

## आवश्यकताएँ

- **OS**: विंडोज़ 10/11
- **पायथन**: 3.10+
- **हार्डवेयर**: एनवीआईडा ग्राफिक्स कार्ड के साथ स्थापित ड्राइवर।
- **CUDA**: टूलकिट 12.x (तनाव परीक्षण/सिमुलेशन सुविधाओं के लिए सख्त रूप से आवश्यक)।

*नोट: यदि CUDA 12.x पहचान नहीं होता है, तो GPU-विशिष्ट तनाव परीक्षण सुविधाएँ अक्षम होंगी।*

---

## स्थापना

उपकरण के लिए कई मॉड्यूलर स्थापना विकल्प उपलब्ध हैं:

### 1. न्यूनतम (केवल CLI)

सर्वर या पृष्ठभूमि निगरानी के लिए सर्वोत्तम, जो कि सिस्टम/GPU मेट्रिक्स प्रदान करता है।

### 2. मानक (CLI + वेब UI)

अधिकांश उपयोगकर्ताओं के लिए सर्वोत्तम।

- वास्तविक समय चार्ट्स के साथ वेब डैशबोर्ड शामिल है।
- REST API अंक।

### 3. पूर्ण (मानक + विज़ुअलाइज़ेशन)

विकास और तनाव परीक्षण के लिए सर्वोत्तम।

- **सिमुलेशन** शामिल है।
- PyTorch/CuPy निर्भरताओं के साथ तनाव परीक्षण।

### त्वरित शुरुआत

1. **डाउनलोड** नवीनतम रिलीज़ या रिपॉजिटरी क्लोन करें।
2. **सेटअप चलाएँ**:

  ```powershell
  .\setup.ps1
  ```

3. **लॉन्च**:

```powershell
# वेब डैशबोर्ड शुरू करें (मानक/पूर्ण)
python health_monitor.py web

# CLI शुरू करें
python health_monitor.py cli
```

---

## लाइसेंस

MIT लाइसेंस। [LICENSE](../LICENSE) देखें विवरण के लिए।