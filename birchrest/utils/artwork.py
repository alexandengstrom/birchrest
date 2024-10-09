def get_artwork(host: str, port: int, version: str) -> str:
    return f"""
\033[91m _      _               _                                  
| |    (_)             | |                           _     
\033[95m| |__   _   ____  ____ | |__    ____  _____   ___  _| |_   
|  _ \\ | | / ___)/ ___)|  _ \\  / ___)| ___ | /___)(_   _)  
\033[96m| |_) )| || |   ( (___ | | | || |    | ____||___ |  | |_   
|____/ |_||_|    \\____)|_| |_||_|    |_____)(___/    \\__)  
                                                           
\033[93mBirchrest v{version}\033[0m

Contribute to the project: 
\033[94mhttps://github.com/alexandengstrom/birchrest\033[0m

\033[92mStarting server...
"""
