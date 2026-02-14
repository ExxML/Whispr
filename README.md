# whispr
Your live AI programming assistant

Compile .exe using Nuitka
```bash
python -m nuitka --standalone --windows-icon-from-ico="src/assets/whispr.ico" --windows-console-mode=disable --enable-plugin=pyqt6 --include-data-dir="src/assets=src/assets" --include-data-dir="src/data=src/data" src/whispr.py
```
> [!NOTE]
> Due to the large google.genai library, the first compilation will take a long time (20-30 minutes using Nuitka).
> Subsequent compilations will be faster due to cached files in the build directory.
