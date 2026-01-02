import subprocess
from pathlib import Path

VIDEO_IDS = [
    "Ky1WodwYUA8","il0dFcWBev0","J2fol8eWo64","KXjccJm-06I",
    "sCiD-Wzj9P0","KP42CpCCGmo","pzcbRNLNkhY","vB1HPzvpMVA",
    "9yuSAKLriAU","eSbeub2ZeNk","2fGyi4ZSHLM","UAjzFTGlaXw",
    "jE7Xa7BYe14","aZUn-WCnkvI","zPi6_uiwabI","7D6KyFZ5NyU",
    "TzvxBbv1eTI","vwCRQS-boMA","RocyCm4edNI","JfPkLAKfNsc",
    "WcaD-o5JGQU","Cn6juk073uM","LOAiJHW_bMA","q73YarcU3lA",
    "8cf_bveteOE","cxAoYd3CXao","LWS51sLnL90","YhmtBmyQt18",
    "kENEXflpUGw","FDz1ZcvUWpI","KUPceyLgzeU","EibDfhzNvzg",
    "Z7Wg1tdgx9I","N0go7bRXvfs","WPBXvDS-UEo","GUJuidMl5ls",
    "aEivWuMUjzM","g93XqSRxcAs","oZICi5W8JIo","T1TmHvJBUc",
    "FLAzwdj2Ncw","cliZ-VzQxkE","1-Ic_HtNS_U","Rq9GYPPkwPY",
    "SR5NYCdzKkc","kV37p-VLh9s","PAiT0Hg_R1Y","e0FvoOtdAQc",
    "YwrapdgMKqI","qvpbO5Y9jN0"
]

AUDIO_DIR = Path(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\audio_downloads")
AUDIO_DIR.mkdir(exist_ok=True)

for vid in VIDEO_IDS:
    out = AUDIO_DIR / f"{vid}.mp3"
    cmd = f'yt-dlp -x --audio-format mp3 -o "{out}" "https://www.youtube.com/watch?v={vid}"'
    print(f"Downloading {vid}...")
    subprocess.run(cmd, shell=True)
