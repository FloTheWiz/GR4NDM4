import sys
import logging
from pathlib import Path
from bot import grandma


banner_str = """
 ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓███████▓▒░░▒▓██████████████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒▒▓███▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
 ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
"""

version_str = """
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░   ░▒▓████▓▒░ 
 ░▒▓█▓▒▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
 ░▒▓█▓▒▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
  ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
  ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░▒▓██▓▒░▒▓█▓▒░ 
   ░▒▓██▓▒░         ░▒▓████████▓▒░▒▓██▓▒░▒▓█▓▒░ 
                                                
"""

COGS = ['stats','wiki','admin']
SECRETS_PATH = Path("core/secrets.env")


def get_secrets():
    secrets = {}
    with open(SECRETS_PATH) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            if "export" not in line:
                continue
            key, value = line.replace("export ", "", 1).strip().split("=", 1)
            secrets[key] = value
        return secrets
        
def main():
    print(banner_str)
    print("="*80)
    print(version_str)
    print("="*80)
    if not SECRETS_PATH.exists():
        print(
            "Error: Have you placed the discord token inside a secrets.env file in /core ?"
        )
    SECRETS = get_secrets()
    client = grandma(COGS, SECRETS)
    client.run(SECRETS["TOKEN"])
    return
        
        
       

if __name__ == "__main__":
    main()
    
  